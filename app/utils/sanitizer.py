# app/utils/sanitizer.py

import bleach

# Define exactly what markup you’ll allow
ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'ul', 'ol', 'li', 'br']
ALLOWED_ATTRS = {}  # no tag-specific attributes


def clean_html(raw_html: str) -> str:
    """
    Strip out any HTML tags/attributes not in your whitelist.
    Returns safe HTML or plain text.
    """
    return bleach.clean(
        raw_html or "",
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True,          # remove disallowed tags completely
        strip_comments=True  # remove HTML comments
    )
