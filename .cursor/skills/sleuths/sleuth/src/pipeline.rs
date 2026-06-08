use crate::chunk::IndexedChunk;
use crate::config::ProcessingConfig;
use crate::context_budget::{group_by_budget, group_chunks_by_budget};
use crate::inference::InferenceClient;
use crate::jsonl_extract::extract_lines;
use crate::prompts::{
    content_budget, merge_prompt, merge_prompt_overhead, relevance_prompt,
    relevance_prompt_overhead, summarize_prompt, summarize_prompt_overhead,
};
use crate::query::SleuthQuery;
use crate::relevance::parse_relevant_ids;
use crate::token::estimate_tokens;
use anyhow::Result;
use std::path::Path;

pub fn stream_chunks(
    path: &Path,
    start_line: u64,
    end_line: u64,
    chunk_lines: u64,
) -> Result<Vec<IndexedChunk>> {
    let mut chunks = Vec::new();
    let mut line = start_line;
    let mut index = 0usize;

    while line <= end_line {
        let chunk_end = (line + chunk_lines - 1).min(end_line);
        let text = extract_lines(path, line, chunk_end)?;
        line = chunk_end + 1;

        if text.trim().is_empty() {
            continue;
        }

        chunks.push(IndexedChunk { index, text });
        index += 1;
    }

    Ok(chunks)
}

pub fn run_relevance_pass(
    client: &InferenceClient,
    query: &SleuthQuery,
    chunks: &[IndexedChunk],
    processing: &ProcessingConfig,
    session_tag: &str,
) -> Result<Vec<IndexedChunk>> {
    let overhead = relevance_prompt_overhead(query, session_tag);
    let budget = content_budget(processing, overhead);
    let max_items = processing.max_chunks_per_batch as usize;
    let groups = group_chunks_by_budget(chunks.to_vec(), budget, max_items);

    let mut relevant = Vec::new();

    for group in groups {
        let indexed: Vec<(usize, &str)> = group
            .iter()
            .map(|c| (c.index, c.text.as_str()))
            .collect();
        let prompt = relevance_prompt(query, &indexed, session_tag);
        let response = client.generate(&prompt)?;
        let max_idx = group.last().map(|c| c.index).unwrap_or(0);
        let ids = parse_relevant_ids(&response, max_idx);

        for c in &group {
            if ids.contains(&c.index) {
                relevant.push(c.clone());
            }
        }
    }

    Ok(relevant)
}

pub fn run_summarize_pass(
    client: &InferenceClient,
    query: &SleuthQuery,
    relevant: &[IndexedChunk],
    processing: &ProcessingConfig,
    session_tag: &str,
) -> Result<Vec<String>> {
    if relevant.is_empty() {
        return Ok(vec![]);
    }

    let overhead =
        summarize_prompt_overhead(query, session_tag, processing.pass_summary_cap_tokens);
    let budget = content_budget(processing, overhead);
    let max_items = processing.max_chunks_per_batch as usize;
    let groups = group_chunks_by_budget(relevant.to_vec(), budget, max_items);

    let mut pass_summaries = Vec::new();

    for group in groups {
        let indexed: Vec<(usize, &str)> = group
            .iter()
            .map(|c| (c.index, c.text.as_str()))
            .collect();
        let prompt = summarize_prompt(
            query,
            &indexed,
            session_tag,
            processing.pass_summary_cap_tokens,
        );
        let summary = client.generate(&prompt)?;
        if !summary.trim().is_empty() {
            pass_summaries.push(summary);
        }
    }

    Ok(pass_summaries)
}

pub fn recursive_reduce(
    client: &InferenceClient,
    query: &SleuthQuery,
    mut summaries: Vec<String>,
    processing: &ProcessingConfig,
    session_tag: &str,
    seed_aggregate: Option<&str>,
) -> Result<String> {
    if summaries.is_empty() {
        return Ok(String::new());
    }

    if summaries.len() == 1 && estimate_tokens(&summaries[0]) <= processing.final_summary_target_tokens
    {
        return Ok(summaries.into_iter().next().unwrap_or_default());
    }

    let target = processing.final_summary_target_tokens;
    let max_items = processing.max_chunks_per_batch as usize;

    while summaries.len() > 1
        || (summaries.len() == 1 && estimate_tokens(&summaries[0]) > target)
    {
        let overhead = merge_prompt_overhead(
            query,
            session_tag,
            target,
            seed_aggregate.is_some(),
        );
        let budget = content_budget(processing, overhead);
        let groups = group_by_budget(std::mem::take(&mut summaries), budget, max_items);

        let mut next = Vec::new();
        for group in groups {
            let prompt = merge_prompt(
                query,
                &group,
                session_tag,
                target,
                seed_aggregate,
            );
            let merged = client.generate(&prompt)?;
            if !merged.trim().is_empty() {
                next.push(merged);
            }
        }

        if next.is_empty() {
            break;
        }
        summaries = next;
    }

    Ok(summaries.into_iter().next().unwrap_or_default())
}

pub fn process_segment_pipeline(
    client: &InferenceClient,
    query: &SleuthQuery,
    transcript_path: &Path,
    start_line: u64,
    end_line: u64,
    processing: &ProcessingConfig,
    session_tag: &str,
) -> Result<String> {
    let chunks = stream_chunks(
        transcript_path,
        start_line,
        end_line,
        processing.chunk_lines,
    )?;

    if chunks.is_empty() {
        return Ok(String::new());
    }

    let relevant = run_relevance_pass(client, query, &chunks, processing, session_tag)?;
    let pass_summaries =
        run_summarize_pass(client, query, &relevant, processing, session_tag)?;

    recursive_reduce(client, query, pass_summaries, processing, session_tag, None)
}

/// Body text after the title header in summary.md.
pub fn summary_body(summary: &str) -> Option<String> {
    let body = summary.lines().skip(1).collect::<Vec<_>>().join("\n");
    let trimmed = body.trim();
    if trimmed.is_empty() {
        None
    } else {
        Some(trimmed.to_string())
    }
}

pub fn merge_into_summary_header(query: &SleuthQuery, body: &str) -> String {
    format!("# {}\n\n{}", query.description, body.trim())
}
