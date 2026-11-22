"""Vercel entry point: serves the same SmartStudy web app and /api/* routes as `python3 -m smartstudy.app`."""
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
from smartstudy.app import Handler  # noqa: E402


class handler(Handler):
    """vercel.json rewrites every path to /api/index?__p=<original path>; restore the original path first."""

    def _restore_path(self):
        u = urlparse(self.path)
        q = parse_qs(u.query, keep_blank_values=True)
        if "__p" in q:
            rest = urlencode({k: v for k, v in q.items() if k != "__p"}, doseq=True)
            self.path = "/" + q["__p"][0].lstrip("/") + ("?" + rest if rest else "")

    def do_GET(self):
        self._restore_path()
        super().do_GET()

    def do_POST(self):
        self._restore_path()
        super().do_POST()
