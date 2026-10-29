"""Blitz TokyoInsider Scraper API — Author: Blitz (@blitzlabx)"""
"""Port of the site inline cipher: ROT13 -> reverse -> base64 -> XOR."""
import base64
import re

from .errors import DecodeError

_ROT13 = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm",
)

_KEY_RE = re.compile(r"""r13\(\s*(['\"])([A-Za-z0-9+/=_\-]+)\1""")


def r13(value: str) -> str:
    return value.translate(_ROT13)


def extract_key(html: str) -> str:
    match = _KEY_RE.search(html)
    if not match:
        raise DecodeError("per-page key not present in page source")
    return r13(match.group(2)[::-1])


def decode_link(part_a: str, part_b: str, key: str) -> str:
    payload = r13((part_a + part_b)[::-1])
    payload += "=" * (-len(payload) % 4)
    try:
        raw = base64.b64decode(payload)
    except Exception as exc:  # noqa: BLE001
        raise DecodeError(f"base64 stage failed: {exc}") from exc
    out = bytes(byte ^ ord(key[i % len(key)]) for i, byte in enumerate(raw))
    url = out.decode("utf-8", "replace").strip()
    if not url.startswith("http"):
        raise DecodeError(f"decoded payload is not a URL: {url[:120]}")
    return url
