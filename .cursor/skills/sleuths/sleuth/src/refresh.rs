use crate::checkpoint::{checkpoint_path, Checkpoint, SegmentKey};
use crate::config::{load_config, sleuths_dir, SleuthsConfig};
use crate::discover::{discover_segments, resolve_slugs, TranscriptSegment};
use crate::jsonl_extract::{count_lines, extract_lines};
use crate::ollama::{map_prompt, reduce_prompt, OllamaClient};
use anyhow::{Context, Result};
use std::path::Path;

const CHUNK_LINES: u64 = 40;

#[derive(Debug, serde::Deserialize)]
pub struct SleuthQuery {
    pub id: String,
    pub description: String,
    pub prompt: String,
}

pub fn load_query(project_root: &Path, sleuth_id: &str) -> Result<SleuthQuery> {
    let path = sleuths_dir(project_root)
        .join("queries")
        .join(format!("{sleuth_id}.yaml"));
    let raw = std::fs::read_to_string(&path)
        .with_context(|| format!("read sleuth query {}", path.display()))?;
    let mut q: SleuthQuery = serde_yaml::from_str(&raw)?;
    if q.id.is_empty() {
        q.id = sleuth_id.to_string();
    }
    Ok(q)
}

pub fn list_sleuth_ids(project_root: &Path) -> Result<Vec<String>> {
    let dir = sleuths_dir(project_root).join("queries");
    if !dir.is_dir() {
        return Ok(vec![]);
    }
    let mut ids = Vec::new();
    for entry in std::fs::read_dir(&dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|e| e.to_str()) == Some("yaml") {
            if let Some(stem) = path.file_stem().and_then(|s| s.to_str()) {
                ids.push(stem.to_string());
            }
        }
    }
    ids.sort();
    Ok(ids)
}

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
        format!("# {}\n\n", query.description)
    };

    let client = OllamaClient::new(config.ollama.clone())?;

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

    for work in pending {
        process_segment(
            &client,
            &query,
            &work.segment,
            work.start_line,
            work.end_line,
            &mut summary,
            &mut checkpoint,
        )?;
        checkpoint.save(&ckpt_path)?;
        std::fs::write(&summary_path, &summary)?;
    }

    Ok(())
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

fn process_segment(
    client: &OllamaClient,
    query: &SleuthQuery,
    seg: &TranscriptSegment,
    start_line: u64,
    end_line: u64,
    summary: &mut String,
    checkpoint: &mut Checkpoint,
) -> Result<()> {
    let session_tag = session_tag(seg);
    let mut line = start_line;

    while line <= end_line {
        let chunk_end = (line + CHUNK_LINES - 1).min(end_line);
        let chunk = extract_lines(&seg.absolute_path, line, chunk_end)?;
        line = chunk_end + 1;

        if chunk.trim().is_empty() {
            continue;
        }

        let map_out = client.generate(&map_prompt(
            &query.prompt,
            &chunk,
            &session_tag,
        ))?;

        if map_out.trim() == "NO_MATCH" || map_out.trim().is_empty() {
            continue;
        }

        *summary = client.generate(&reduce_prompt(
            &query.prompt,
            summary,
            &map_out,
            &session_tag,
        ))?;
    }

    checkpoint.upsert_segment(
        SegmentKey {
            transcript_id: seg.transcript_id.clone(),
            relative_path: seg.relative_path.clone(),
        },
        end_line,
    );

    Ok(())
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
