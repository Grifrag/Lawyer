import os
from cryptography.fernet import Fernet

# Module-level cached key so encrypt/decrypt always use the same key within a process.
# If FERNET_KEY is not set (dev/test), a stable per-process key is generated once.
_FERNET_KEY = os.environ.get("FERNET_KEY")
if not _FERNET_KEY:
    _FERNET_KEY = Fernet.generate_key().decode()
_fernet = Fernet(_FERNET_KEY.encode() if isinstance(_FERNET_KEY, str) else _FERNET_KEY)

def encrypt(value: str) -> str:
    return _fernet.encrypt(value.encode()).decode()

def decrypt(value: str) -> str:
    return _fernet.decrypt(value.encode()).decode()
