"""SmartStudy - lecture notes -> grounded summary, key terms and practice questions (Problem C2)."""
from __future__ import annotations
__version__ = "0.2.0"


def _load_dotenv():
    """Read KEY=value lines from <repo>/.env into os.environ (without overriding real environment variables)."""
    import os
    from pathlib import Path
    f = Path(__file__).resolve().parent.parent.parent / ".env"
    try:
        for line in f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    except OSError:
        pass


_load_dotenv()
