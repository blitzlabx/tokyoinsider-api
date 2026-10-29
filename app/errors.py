"""Blitz TokyoInsider Scraper API — Author: Blitz (@blitzlabx)"""
class UpstreamError(Exception):
    status = 502
    code = "upstream_error"


class UpstreamBlocked(UpstreamError):
    status = 503
    code = "cloudflare_blocked"


class NotFound(UpstreamError):
    status = 404
    code = "not_found"


class DecodeError(UpstreamError):
    status = 502
    code = "decode_failed"
