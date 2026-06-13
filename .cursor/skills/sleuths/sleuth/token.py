"""Approximate token count for budget packing (ceil(chars / 4))."""


def estimate_tokens(text: str) -> int:
    chars = len(text)
    if chars == 0:
        return 0
    return (chars + 3) // 4


def truncate_prefix_to_tokens(text: str, max_tokens: int) -> tuple[str, str]:
    if max_tokens == 0:
        return "", text
    if estimate_tokens(text) <= max_tokens:
        return text, ""

    max_chars = max_tokens * 4
    prefix = text[:max_chars]
    remainder = text[max_chars:]
    return prefix, remainder
