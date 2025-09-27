from urllib.parse import urlparse


def get_domain_from_url(url: str) -> str | None:
    """Extracts the hostname (domain) from a full URL."""
    try:
        return urlparse(url).hostname
    except Exception:
        return None


def get_favicon_url(domain: str | None, size: int = 64) -> str | None:
    """
    Generates a URL to a favicon provider.
    Using Google's is a reliable, free option.
    """
    if not domain:
        return None
    return f"https://www.google.com/s2/favicons?domain={domain}&sz={size}"
