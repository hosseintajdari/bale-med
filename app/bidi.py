import re

# Unicode bidi isolates keep Latin segments readable inside Persian text.
LRI = "\u2066"  # Left-to-Right Isolate
PDI = "\u2069"  # Pop Directional Isolate

_LTR_SEGMENT = re.compile(
    r"https?://[^\s]+"
    r"|/[A-Za-z0-9_\-/]+"
    r"|[A-Za-z0-9][A-Za-z0-9._\-]*"
)


def format_mixed_direction_text(text: str) -> str:
    """Wrap Latin commands, paths, and URLs so mixed Persian/English lines render correctly."""
    if not text:
        return text

    def wrap(match: re.Match[str]) -> str:
        return f"{LRI}{match.group(0)}{PDI}"

    return _LTR_SEGMENT.sub(wrap, text)
