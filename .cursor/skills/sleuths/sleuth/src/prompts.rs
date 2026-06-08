use crate::config::ProcessingConfig;
use crate::query::SleuthQuery;
use crate::token::estimate_tokens;

pub fn relevance_prompt(
    query: &SleuthQuery,
    indexed_chunks: &[(usize, &str)],
    session_tag: &str,
) -> String {
    let mut body = String::new();
    for (idx, text) in indexed_chunks {
        body.push_str(&format!("\n--- chunk {idx} ---\n{text}\n"));
    }
    format!(
        r#"You are filtering Cursor agent transcript chunks for relevance to a sleuth lens.

Sleuth topic: {description}

Lens instructions:
{lens}

Source session: {session_tag}

Each chunk below is labeled with a zero-based index. Respond with ONLY a JSON object (no prose, no markdown fences) listing indices of chunks whose content is relevant to the sleuth topic:

{{"relevant_ids": [0, 2]}}

If nothing is relevant, respond: {{"relevant_ids": []}}

Indexed chunks:{body}
"#,
        description = query.description,
        lens = query.prompt,
    )
}

pub fn summarize_prompt(
    query: &SleuthQuery,
    indexed_chunks: &[(usize, &str)],
    session_tag: &str,
    pass_cap_tokens: u64,
) -> String {
    let mut body = String::new();
    for (idx, text) in indexed_chunks {
        body.push_str(&format!("\n--- chunk {idx} ---\n{text}\n"));
    }
    format!(
        r#"You are summarizing relevant Cursor agent transcript chunks for a sleuth lens.

Sleuth topic: {description}

Lens instructions:
{lens}

Source session: {session_tag}

Produce a markdown bullet summary of facts present in the chunks that match the lens.
Keep the summary under approximately {pass_cap_tokens} tokens.
Quote file paths and identifiers verbatim. Do not invent details.

Relevant chunks:{body}
"#,
        description = query.description,
        lens = query.prompt,
    )
}

pub fn merge_prompt(
    query: &SleuthQuery,
    summaries: &[String],
    session_tag: &str,
    target_cap_tokens: u64,
    seed_aggregate: Option<&str>,
) -> String {
    let mut body = String::new();
    for (i, s) in summaries.iter().enumerate() {
        body.push_str(&format!("\n--- summary {i} ---\n{s}\n"));
    }
    let seed_section = seed_aggregate
        .filter(|s| !s.trim().is_empty())
        .map(|seed| {
            format!(
                r#"
Prior aggregate summary (use as the starting merged document; deduplicate against new material):
{seed}
"#
            )
        })
        .unwrap_or_default();

    format!(
        r#"You are merging sleuth summaries into one consolidated document.

Sleuth topic: {description}

Lens instructions:
{lens}

Source session: {session_tag}
{seed_section}
Summaries to merge:{body}

Instructions:
- Deduplicate overlapping facts; prefer one clear bullet per fact.
- Preserve concrete file paths and identifiers from sources.
- Use markdown bullet lists.
- Keep the merged result under approximately {target_cap_tokens} tokens.
"#,
        description = query.description,
        lens = query.prompt,
    )
}

pub fn relevance_prompt_overhead(query: &SleuthQuery, session_tag: &str) -> u64 {
    estimate_tokens(&relevance_prompt(query, &[], session_tag))
}

pub fn summarize_prompt_overhead(
    query: &SleuthQuery,
    session_tag: &str,
    pass_cap_tokens: u64,
) -> u64 {
    estimate_tokens(&summarize_prompt(query, &[], session_tag, pass_cap_tokens))
}

pub fn merge_prompt_overhead(
    query: &SleuthQuery,
    session_tag: &str,
    target_cap_tokens: u64,
    has_seed: bool,
) -> u64 {
    let seed = if has_seed { Some("") } else { None };
    estimate_tokens(&merge_prompt(
        query,
        &[],
        session_tag,
        target_cap_tokens,
        seed,
    ))
}

pub fn content_budget(processing: &ProcessingConfig, prompt_overhead: u64) -> u64 {
    processing
        .context_budget_tokens
        .saturating_sub(processing.response_headroom_tokens)
        .saturating_sub(prompt_overhead)
}
