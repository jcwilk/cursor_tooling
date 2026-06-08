use crate::chunk::IndexedChunk;
use crate::token::{estimate_tokens, truncate_prefix_to_tokens};

/// Partition indexed transcript chunks into budget-fitting groups (preserves order).
pub fn group_chunks_by_budget(
    chunks: Vec<IndexedChunk>,
    available_budget: u64,
    max_items: usize,
) -> Vec<Vec<IndexedChunk>> {
    if chunks.is_empty() {
        return vec![];
    }
    if available_budget == 0 {
        return vec![chunks];
    }

    let mut groups: Vec<Vec<IndexedChunk>> = Vec::new();
    let mut pending = chunks;

    while !pending.is_empty() {
        let mut group: Vec<IndexedChunk> = Vec::new();
        let mut group_tokens: u64 = 0;

        while !pending.is_empty() {
            if max_items > 0 && group.len() >= max_items {
                break;
            }

            let item = pending.remove(0);
            let item_tokens = estimate_tokens(&item.text);

            if group.is_empty() && item_tokens > available_budget {
                let (prefix, remainder) =
                    truncate_prefix_to_tokens(&item.text, available_budget);
                if !prefix.is_empty() {
                    eprintln!(
                        "context-budget: truncated chunk {} ({} → {} est. tokens)",
                        item.index,
                        item_tokens,
                        estimate_tokens(&prefix)
                    );
                    group.push(IndexedChunk {
                        index: item.index,
                        text: prefix,
                    });
                }
                if !remainder.is_empty() {
                    pending.insert(
                        0,
                        IndexedChunk {
                            index: item.index,
                            text: remainder,
                        },
                    );
                }
                break;
            }

            if group_tokens + item_tokens <= available_budget {
                group_tokens += item_tokens;
                group.push(item);
                continue;
            }

            if group.len() > 1 {
                pending.insert(0, item);
                break;
            }

            pending.insert(0, item);
            break;
        }

        if !group.is_empty() {
            groups.push(group);
        } else if !pending.is_empty() {
            let stuck = pending.remove(0);
            eprintln!(
                "context-budget: dropping stuck chunk {} — budget {}",
                stuck.index, available_budget
            );
        }
    }

    groups
}

/// Partition ordered text items into groups that fit `available_budget` (content only;
/// caller subtracts prompt overhead and response headroom first).
pub fn group_by_budget(
    items: Vec<String>,
    available_budget: u64,
    max_items: usize,
) -> Vec<Vec<String>> {
    if items.is_empty() {
        return vec![];
    }
    if available_budget == 0 {
        return vec![];
    }

    let mut groups: Vec<Vec<String>> = Vec::new();
    let mut pending: Vec<String> = items;

    while !pending.is_empty() {
        let mut group: Vec<String> = Vec::new();
        let mut group_tokens: u64 = 0;

        while !pending.is_empty() {
            if max_items > 0 && group.len() >= max_items {
                break;
            }

            let item = pending.remove(0);
            let item_tokens = estimate_tokens(&item);

            if group.is_empty() && item_tokens > available_budget {
                let (prefix, remainder) = truncate_prefix_to_tokens(&item, available_budget);
                if !prefix.is_empty() {
                    eprintln!(
                        "context-budget: truncated oversized item ({} → {} est. tokens)",
                        item_tokens,
                        estimate_tokens(&prefix)
                    );
                    group.push(prefix);
                }
                if !remainder.is_empty() {
                    pending.insert(0, remainder);
                }
                break;
            }

            if group_tokens + item_tokens <= available_budget {
                group_tokens += item_tokens;
                group.push(item);
                continue;
            }

            if group.len() > 1 {
                pending.insert(0, item);
                break;
            }

            pending.insert(0, item);
            break;
        }

        if !group.is_empty() {
            groups.push(group);
        } else if !pending.is_empty() {
            let stuck = pending.remove(0);
            eprintln!(
                "context-budget: dropping stuck item ({} est. tokens) — budget {}",
                estimate_tokens(&stuck),
                available_budget
            );
        }
    }

    groups
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::token::estimate_tokens;

    fn item(chars: usize) -> String {
        "x".repeat(chars)
    }

    fn chunk(index: usize, chars: usize) -> IndexedChunk {
        IndexedChunk {
            index,
            text: item(chars),
        }
    }

    #[test]
    fn single_oversized_item_splits() {
        let big = item(100);
        let groups = group_by_budget(vec![big.clone()], 10, 20);
        assert!(groups.len() >= 2);
        let joined: String = groups.into_iter().flatten().collect();
        assert_eq!(joined.len(), big.len());
    }

    #[test]
    fn exact_fit_single_group() {
        let a = item(4);
        let b = item(4);
        let budget = estimate_tokens(&a) + estimate_tokens(&b);
        let groups = group_by_budget(vec![a, b], budget, 20);
        assert_eq!(groups.len(), 1);
        assert_eq!(groups[0].len(), 2);
    }

    #[test]
    fn multi_group_split_on_overflow() {
        let a = item(16);
        let b = item(16);
        let c = item(16);
        let one = estimate_tokens(&a);
        let budget = one * 2;
        let groups = group_by_budget(vec![a, b, c], budget, 20);
        assert!(groups.len() >= 2);
        let total: usize = groups.iter().map(|g| g.len()).sum();
        assert_eq!(total, 3);
    }

    #[test]
    fn count_cap_splits_token_fitting_group() {
        let chunks: Vec<IndexedChunk> = (0..5).map(|i| chunk(i, 4)).collect();
        let budget = estimate_tokens(&item(4)) * 10;
        let groups = group_chunks_by_budget(chunks, budget, 2);
        assert_eq!(groups.len(), 3);
        assert_eq!(groups[0].len(), 2);
        assert_eq!(groups[1].len(), 2);
        assert_eq!(groups[2].len(), 1);
    }
}
