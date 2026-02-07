import logging
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


def _keepalive_loop(url: str, interval: int, timeout: int) -> None:
    req = Request(url, headers={"User-Agent": "keepalive/1.0"})
    while True:
        try:
            with urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", None)
                logger.debug("keepalive: %s -> %s", url, status)
        except (HTTPError, URLError) as e:
            logger.warning("keepalive failed for %s: %s", url, e)
        except Exception as e:
            logger.exception("unexpected keepalive error for %s: %s", url, e)
        time.sleep(interval)


def start_keepalive(url: str, interval_seconds: int = 180, timeout_seconds: int = 10) -> threading.Thread:
    """
    Start a background daemon thread that pings `url` every `interval_seconds`.

    Returns the started Thread object so the caller can keep a reference if desired.
    """
    thread = threading.Thread(
        target=_keepalive_loop,
        args=(url, interval_seconds, timeout_seconds),
        daemon=True,
        name=f"keepalive-{int(time.time())}",
    )
    thread.start()
    logger.info("keepalive thread started for %s (interval=%ss)", url, interval_seconds)
    return thread


def ping_once(url: str, timeout_seconds: int = 10) -> int | None:
    """Perform a single GET to `url`. Returns HTTP status code or None on error."""
    try:
        req = Request(url, headers={"User-Agent": "keepalive/1.0"})
        with urlopen(req, timeout=timeout_seconds) as resp:
            return getattr(resp, "status", None)
    except Exception as e:
        logger.debug("keepalive.ping_once failed for %s: %s", url, e)
        return None
