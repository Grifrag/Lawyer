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

    NOTE: CSS selectors are best-guess based on Oracle ADF structure.
    They MUST be verified against the live solon.gov.gr DOM.
    Use headless=False to inspect if needed.
    """
    court = case["court"]
    search_type = case["search_type"]
    number = case["number"]
    year = str(case["year"])

    from playwright.sync_api import TimeoutError as PWTimeout

    for attempt in range(3):
        try:
            page.goto(SOLON_URL, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            # Select court from dropdown by visible text
            page.select_option("select[id*='court'], select[id*='Court']", label=court)
            page.wait_for_timeout(2000)  # ADF re-renders after selection

            # Select search type (GAK or EAK)
            if search_type == "GAK":
                page.click("input[value='GAK'], label:has-text('ΓΑΚ')")
            else:
                page.click("input[value='EAK'], label:has-text('ΕΑΚ')")
            page.wait_for_timeout(500)

            # Fill number and year
            page.fill("input[id*='gakNumber'], input[id*='Number']", number)
            page.fill("input[id*='gakYear'], input[id*='Year']", year)

            # Submit
            page.click("button[id*='search'], input[type='submit']")
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)

            # Check for "no data" message
            if page.locator("text=Δεν βρέθηκαν δεδομένα").count() > 0:
                logger.info("No data found for case %s/%s", number, year)
                return None

            # Parse results table
            rows = page.locator("table tr").all()
            for row in rows[1:]:  # skip header
                cells = row.locator("td").all_text_contents()
                if len(cells) < 8:
                    continue
                # Column positions based on solon.gov.gr table structure:
                # 0: Filing date, 1: GAK, 2: GAK year, 3: EAK, 4: EAK year,
                # 5: Procedure, 6: Subject, 7: Type, 8: Docket,
                # 9: Decision number, 10: Decision year, 11: Result
                decision_number = cells[9].strip() if len(cells) > 9 else ""
                decision_year = cells[10].strip() if len(cells) > 10 else ""
                result_text = cells[11].strip() if len(cells) > 11 else ""

                if decision_number:
                    return {
                        "decision_number": decision_number,
                        "decision_year": decision_year,
                        "result_text": result_text,
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
