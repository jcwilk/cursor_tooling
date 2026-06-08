/// Approximate token count for budget packing (ceil(chars / 4)).
pub fn estimate_tokens(text: &str) -> u64 {
    let chars = text.chars().count() as u64;
    if chars == 0 {
        return 0;
    }
    (chars + 3) / 4
}

/// Largest prefix of `text` whose estimated tokens are at most `max_tokens`.
pub fn truncate_prefix_to_tokens(text: &str, max_tokens: u64) -> (String, String) {
    if max_tokens == 0 {
        return (String::new(), text.to_string());
    }
    if estimate_tokens(text) <= max_tokens {
        return (text.to_string(), String::new());
    }

    let max_chars = (max_tokens * 4) as usize;
    let prefix: String = text.chars().take(max_chars).collect();
    let remainder: String = text.chars().skip(max_chars).collect();
    (prefix, remainder)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_is_zero() {
        assert_eq!(estimate_tokens(""), 0);
    }

    #[test]
    fn four_chars_is_one_token() {
        assert_eq!(estimate_tokens("abcd"), 1);
        assert_eq!(estimate_tokens("abcde"), 2);
    }
}
