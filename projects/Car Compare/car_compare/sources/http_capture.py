"""Isolated public Visor fetch; the parent owns and bounds this process."""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

MAX_RESPONSE_BYTES = 8 * 1024 * 1024


def allowed(url):
    parts = urllib.parse.urlsplit(url)
    return parts.scheme == "https" and parts.hostname == "visor.vin" and parts.port in (None, 443) and not parts.username


class VisorRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        if not allowed(url):
            raise ValueError("Visor redirect left the allowed public host")
        return super().redirect_request(request, response, code, message, headers, url)


def capture(payload):
    url = payload["url"]
    if not allowed(url):
        raise ValueError("Only the public Visor HTTPS host is allowed")
    request = urllib.request.Request(url, headers=payload["headers"])
    opener = urllib.request.build_opener(VisorRedirects())
    try:
        with opener.open(request, timeout=float(payload["timeout"])) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                raise ValueError("Visor response exceeded the capture size limit")
            return {"status": response.status, "text": body.replace(b"\x00", b"").decode("utf-8", "replace")}
    except urllib.error.HTTPError as exc:
        return {"status": exc.code, "retry_after": exc.headers.get("Retry-After"), "error": str(exc)}


if __name__ == "__main__":
    try:
        print(json.dumps(capture(json.load(sys.stdin))))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)
