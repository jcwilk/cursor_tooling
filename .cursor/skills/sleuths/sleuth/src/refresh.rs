use crate::checkpoint::{checkpoint_path, Checkpoint, SegmentKey};
use crate::config::{load_config, sleuths_dir, SleuthsConfig};
use crate::discover::{discover_segments, resolve_slugs, TranscriptSegment};
use crate::inference::{inference_call_count, reset_inference_call_count, InferenceClient};
use crate::jsonl_extract::count_lines;
use crate::pipeline::{
    merge_into_summary_header, process_segment_pipeline, recursive_reduce, summary_body,
};
use crate::query::{list_sleuth_ids, load_query};
use crate::verbose;
use anyhow::Result;
use std::path::Path;

pub fn refresh_sleuth(project_root: &Path, sleuth_id: &str) -> Result<()> {
    let config = load_config(project_root)?;
    refresh_sleuth_with_config(project_root, sleuth_id, &config)
}

pub fn refresh_all(project_root: &Path) -> Result<()> {
    let config = load_config(project_root)?;
    let ids = list_sleuth_ids(project_root)?;
    if ids.is_empty() {
        anyhow::bail!("no sleuths found under .sleuths/queries/");
    }
    for id in ids {
        refresh_sleuth_with_config(project_root, &id, &config)?;
    }
    Ok(())
}

fn refresh_sleuth_with_config(
    project_root: &Path,
    sleuth_id: &str,
    config: &SleuthsConfig,
) -> Result<()> {
    let query = load_query(project_root, sleuth_id)?;
    let slugs = resolve_slugs(project_root, config)?;
    let segments = discover_segments(&slugs)?;

    let sleuth_dir = sleuths_dir(project_root).join(sleuth_id);
    std::fs::create_dir_all(&sleuth_dir)?;

    let ckpt_path = checkpoint_path(&sleuth_dir);
    let mut checkpoint = Checkpoint::load(&ckpt_path)?;
    let processed = checkpoint.line_count_map();

    let summary_path = sleuth_dir.join("summary.md");
    let mut summary = if summary_path.exists() {
        std::fs::read_to_string(&summary_path)?
    } else {
        merge_into_summary_header(&query, "")
    };

    let client = InferenceClient::new(config.ollama.clone())?;
    let processing = config.processing.clone();
    let prior_body = summary_body(&summary);

    let pending: Vec<_> = segments
        .into_iter()
        .filter_map(|seg| pending_work(&seg, &processed))
        .collect();

    if pending.is_empty() {
        eprintln!("Sleuth '{sleuth_id}': nothing new to process");
        return Ok(());
    }

    eprintln!(
        "Sleuth '{sleuth_id}': processing {} segment(s)",
        pending.len()
    );

    reset_inference_call_count();
    let mut new_segment_summaries: Vec<String> = Vec::new();

    for (segment_idx, work) in pending.iter().enumerate() {
        verbose::log(format!(
            "Sleuth '{sleuth_id}': segment {}/{} {} lines {}-{}",
            segment_idx + 1,
            pending.len(),
            work.segment.relative_path,
            work.start_line,
            work.end_line
        ));
        let session_tag = session_tag(&work.segment);
        let segment_summary = process_segment_pipeline(
            &client,
            &query,
            &work.segment.absolute_path,
            work.start_line,
            work.end_line,
            &processing,
            &session_tag,
        )?;

        if !segment_summary.trim().is_empty() {
            new_segment_summaries.push(segment_summary);
        }

        let body = merge_new_summaries(
            &client,
            &query,
            &processing,
            &session_tag,
            prior_body.as_deref(),
            &new_segment_summaries,
        )?;
        summary = merge_into_summary_header(&query, &body);

        checkpoint.upsert_segment(
            SegmentKey {
                transcript_id: work.segment.transcript_id.clone(),
                relative_path: work.segment.relative_path.clone(),
            },
            work.end_line,
        );
        checkpoint.save(&ckpt_path)?;
        std::fs::write(&summary_path, &summary)?;
        verbose::log(format!(
            "Sleuth '{sleuth_id}': segment {}/{} checkpointed (inference calls so far: {})",
            segment_idx + 1,
            pending.len(),
            inference_call_count()
        ));
    }

    eprintln!(
        "Sleuth '{sleuth_id}': inference calls this refresh: {}",
        inference_call_count()
    );

    Ok(())
}

fn merge_new_summaries(
    client: &InferenceClient,
    query: &crate::query::SleuthQuery,
    processing: &crate::config::ProcessingConfig,
    session_tag: &str,
    prior_body: Option<&str>,
    new_summaries: &[String],
) -> Result<String> {
    if new_summaries.is_empty() {
        return Ok(prior_body.unwrap_or("").to_string());
    }

    if let Some(prior) = prior_body.filter(|s| !s.trim().is_empty()) {
        let mut inputs = vec![prior.to_string()];
        inputs.extend(new_summaries.iter().cloned());
        return recursive_reduce(
            client,
            query,
            inputs,
            processing,
            session_tag,
            Some(prior),
        );
    }

    recursive_reduce(
        client,
        query,
        new_summaries.to_vec(),
        processing,
        session_tag,
        None,
    )
}

struct PendingWork {
    segment: TranscriptSegment,
    start_line: u64,
    end_line: u64,
}

fn pending_work(
    seg: &TranscriptSegment,
    processed: &std::collections::HashMap<SegmentKey, u64>,
) -> Option<PendingWork> {
    let total = count_lines(&seg.absolute_path).ok()?;
    if total == 0 {
        return None;
    }

    let key = SegmentKey {
        transcript_id: seg.transcript_id.clone(),
        relative_path: seg.relative_path.clone(),
    };
    let done = processed.get(&key).copied().unwrap_or(0);
    if done >= total {
        return None;
    }

    Some(PendingWork {
        segment: seg.clone(),
        start_line: done + 1,
        end_line: total,
    })
}

fn session_tag(seg: &TranscriptSegment) -> String {
    if seg.relative_path.starts_with("subagents/") {
        let sub_id = seg
            .relative_path
            .strip_prefix("subagents/")
            .and_then(|p| p.strip_suffix(".jsonl"))
            .unwrap_or(&seg.relative_path);
        format!(
            "[session {}] [subagent {}]",
            seg.transcript_id, sub_id
        )
    } else {
        format!("[session {}]", seg.transcript_id)
    }
}
