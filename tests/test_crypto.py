from app.crypto import decode_link, extract_key, r13

PAGE = 'var K = r13("nprnqp7ro80r".split(\'\').reverse().join(\'\'));'
A = (
    "=ZEPI5EVHMRWtZ1H0OlJXVUHRA1IR1IHFLlV5OjIRAEIMEyHUp1E6IaZMSSDEMyEUNyHXHO"
    "FESSDGHNAUp1Ep9yPARFIGSHRJOjBID1PNNORBjjAUp1EDASOR8jWEMyEmO1EXISQoVDX"
)
B = (
    "wRyELD1HZHtHFkRIDOyINLIGCZtFFkxN44tOxOwPY0OULxjVM1NP/cDCZbUCBWyFIkIHCDIH"
    "KNtIEAIIEE1HUHyHKjINBOIKFkIJQONQJVRNSbtSC0NQB5DQZ5OOVpNNZfRGALuRZEHQ"
)


def test_rot13_roundtrip():
    assert r13(r13("TokyoInsider")) == "TokyoInsider"


def test_key_extraction():
    assert extract_key(PAGE) == "e08be7cdaeca"


def test_decode_link_produces_url():
    url = decode_link(A, B, extract_key(PAGE))
    assert url.startswith("http")
    assert url.endswith(".mkv")
    assert "Lazier" in url
