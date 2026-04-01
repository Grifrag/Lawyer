import logging
import time
from notifier import send_notification

logger = logging.getLogger(__name__)

SOLON_URL = "https://extapps.solon.gov.gr/mojwp/faces/TrackLdoPublic"

# Concurrency guard — prevents overlapping check runs
_check_running = False

# Resource types to block — not needed for scraping, saves ~60% load time
_BLOCKED_RESOURCES = {"image", "media", "font", "stylesheet"}


def _build_decision_link(court, search_type, number, year):
    """Construct a solon.gov.gr URL that pre-fills the search form."""
    return (
        f"{SOLON_URL}?"
        f"court={court}&type={search_type}&number={number}&year={year}"
    )


def _scrape_case(case, page):
    """
    Use an existing Playwright page to search solon.gov.gr for the given case.
    Returns dict with decision info, or None if no decision found.

    Selectors verified against the live solon.gov.gr DOM (Oracle ADF).
    """
    court = case["court"]
    search_type = case["search_type"]
    number = case["number"]
    year = str(case["year"])

    from playwright.sync_api import TimeoutError as PWTimeout

    for attempt in range(3):
        try:
            # wait_until="commit" fires on first response byte — ADF never fires domcontentloaded
            page.goto(SOLON_URL, wait_until="commit")
            page.wait_for_timeout(8000)  # ADF needs time to initialize JS

            # Court dropdown: select[name='courtOfficeOC'] — label match is trimmed by Playwright
            page.select_option("select[name='courtOfficeOC']", label=court)
            page.wait_for_timeout(3000)  # ADF re-renders after court selection

            # Search type radio: value=0 → GAK (default), value=1 → EAK
            if search_type != "GAK":
                page.click("input[name='socSelectedSearchOption'][value='1']")
                page.wait_for_timeout(500)
                # EAK inputs
                page.fill("input[name='it1Eak']", number)
                page.fill("input[name='it2eak']", year)
            else:
                # GAK inputs
                page.fill("input[name='it1']", number)
                page.fill("input[name='it2']", year)

            # Search button is an <a> inside div#ldoSearch
            page.click("#ldoSearch a")
            page.wait_for_timeout(5000)

            # No results: pt_emptyList becomes visible
            if page.locator("#pt_emptyList").is_visible():
                logger.info("No data found for case %s/%s", number, year)
                return None

            # Results: each row has 8 role=gridcell elements
            # [0] GAK/yr, [1] EAK/yr, [2] procedure, [3] subject, [4] type,
            # [5] docket, [6] "decision_num/year - kind", [7] result_text
            gridcells = page.locator("[role='gridcell']").all()
            if not gridcells:
                return None

            cells_per_row = 8
            for i in range(0, len(gridcells), cells_per_row):
                row_cells = gridcells[i:i + cells_per_row]
                if len(row_cells) < 8:
                    continue
                decision_col = row_cells[6].inner_text().strip()
                result_text = row_cells[7].inner_text().strip()

                # decision_col format: "1532/2026 - ΔΕΚΤΗ"
                if decision_col and "/" in decision_col:
                    parts = decision_col.split(" - ", 1)
                    num_year = parts[0].strip().split("/")
                    decision_number = num_year[0].strip()
                    decision_year = num_year[1].strip() if len(num_year) > 1 else ""
                    decision_kind = parts[1].strip() if len(parts) > 1 else ""
                    full_result = f"{result_text} - {decision_kind}" if decision_kind else result_text
                    return {
                        "decision_number": decision_number,
                        "decision_year": decision_year,
                        "result_text": full_result,
                        "decision_link": _build_decision_link(
                            court, search_type, number, year
                        ),
                    }

            return None

        except PWTimeout:
            logger.warning("Timeout on attempt %d for case %s/%s", attempt + 1, number, year)
            if attempt < 2:
                time.sleep(10)
        except Exception as e:
            logger.error("Error scraping case %s/%s: %s", number, year, e)
            if attempt < 2:
                time.sleep(10)

    logger.error("All attempts failed for case %s/%s", number, year)
    return None


def check_case(case, db, notification_config, page=None):
    """Check one case and notify if a new decision is found."""
    logger.info("Checking case: %s %s/%s", case["court"], case["number"], case["year"])

    result = _scrape_case(case, page)
    db.update_last_checked(case["id"])

    if not result:
        return

    is_new = db.upsert_result(
        case_id=case["id"],
        decision_number=result["decision_number"],
        decision_year=result["decision_year"],
        result_text=result["result_text"],
        decision_link=result["decision_link"],
    )

    if not is_new:
        logger.info("Decision %s already known — skipping notification", result["decision_number"])
        return

    result.update({
        "court": case["court"],
        "search_type": case["search_type"],
        "number": case["number"],
        "year": case["year"],
        "description": case.get("description", ""),
    })

    send_notification(
        notification_type=notification_config.get("notification_type"),
        gmail_sender=notification_config.get("gmail_sender"),
        gmail_app_password=notification_config.get("gmail_app_password"),
        gmail_recipient=notification_config.get("gmail_recipient"),
        telegram_bot_token=notification_config.get("telegram_bot_token"),
        telegram_chat_id=notification_config.get("telegram_chat_id"),
        result=result,
    )

    unnotified = db.get_unnotified_results()
    for r in unnotified:
        if r["case_id"] == case["id"] and r["decision_number"] == result["decision_number"]:
            db.mark_notified(r["id"])


def run_all_checks(db, notification_config):
    """
    Check all active cases using a single shared browser instance.
    Blocks images/fonts/CSS for ~3x speed improvement.
    Skips if already running (concurrency guard).
    """
    global _check_running
    if _check_running:
        logger.warning("Check already in progress — skipping.")
        return
    _check_running = True
    try:
        cases = db.get_active_cases()
        logger.info("Starting check for %d active cases", len(cases))

        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_default_timeout(30000)

            # Block images, fonts, media — not needed, saves ~60% load time
            page.route(
                "**/*",
                lambda r: r.abort()
                if r.request.resource_type in _BLOCKED_RESOURCES
                else r.continue_()
            )

            for case in cases:
                check_case(case, db, notification_config, page=page)

            browser.close()

        logger.info("Check complete.")
    finally:
        _check_running = False
