from html import unescape
import nh3


def clean_escaped_html(value: str) -> str:
    """Remove non-whitelist HTML tags from user input.

    Args:
        value (str): string containing HTML

    Returns:
        str: Sanitized HTML
    """
    clean = nh3.clean(
        unescape(value),
        tags={"br", "p", "strong", "em", "u", "ul", "ol", "li"}
    )
    return clean
