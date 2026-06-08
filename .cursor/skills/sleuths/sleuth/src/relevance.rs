#[derive(Debug, serde::Deserialize)]
struct RelevanceResponse {
    #[serde(default)]
    relevant_ids: Vec<serde_json::Value>,
}

/// Parse LLM relevance output into zero-based chunk indices.
/// Invalid JSON, wrong shape, or out-of-range ids are ignored; parse failure → empty.
pub fn parse_relevant_ids(response: &str, max_index: usize) -> Vec<usize> {
    let trimmed = strip_code_fences(response.trim());
    let parsed: RelevanceResponse = match serde_json::from_str(trimmed) {
        Ok(v) => v,
        Err(e) => {
            eprintln!("relevance: failed to parse JSON: {e}");
            return vec![];
        }
    };

    let mut ids = Vec::new();
    for v in parsed.relevant_ids {
        let idx = match v {
            serde_json::Value::Number(n) => n.as_u64().and_then(|u| usize::try_from(u).ok()),
            _ => None,
        };
        let Some(idx) = idx else {
            continue;
        };
        if idx > max_index {
            continue;
        }
        if !ids.contains(&idx) {
            ids.push(idx);
        }
    }
    ids.sort_unstable();
    ids
}

fn strip_code_fences(s: &str) -> &str {
    let s = s.trim();
    if let Some(rest) = s.strip_prefix("```json") {
        return rest.strip_suffix("```").unwrap_or(rest).trim();
    }
    if let Some(rest) = s.strip_prefix("```") {
        return rest.strip_suffix("```").unwrap_or(rest).trim();
    }
    s
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_valid_ids() {
        let ids = parse_relevant_ids(r#"{"relevant_ids": [0, 2, 5]}"#, 5);
        assert_eq!(ids, vec![0, 2, 5]);
    }

    #[test]
    fn ignores_out_of_range() {
        let ids = parse_relevant_ids(r#"{"relevant_ids": [0, 99]}"#, 3);
        assert_eq!(ids, vec![0]);
    }

    #[test]
    fn strips_fences() {
        let raw = "```json\n{\"relevant_ids\": [1]}\n```";
        let ids = parse_relevant_ids(raw, 3);
        assert_eq!(ids, vec![1]);
    }

    #[test]
    fn parse_failure_empty() {
        assert!(parse_relevant_ids("not json", 3).is_empty());
    }
}
