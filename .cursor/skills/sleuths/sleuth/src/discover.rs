use crate::config::{cursor_projects_dir, SleuthsConfig};
use crate::slug::slug_from_path;
use anyhow::{Context, Result};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::SystemTime;

#[derive(Debug, Clone)]
pub struct TranscriptSegment {
    pub transcript_id: String,
    pub relative_path: String,
    pub absolute_path: PathBuf,
    pub mtime: SystemTime,
}

pub fn resolve_slugs(project_root: &Path, config: &SleuthsConfig) -> Result<Vec<String>> {
    let mut slugs = vec![slug_from_path(project_root)];

    if project_root.join(".git").exists() {
        if let Ok(extra) = git_worktree_paths(project_root) {
            for path in extra {
                let s = slug_from_path(&path);
                if !slugs.contains(&s) {
                    slugs.push(s);
                }
            }
        }
    }

    for s in &config.transcripts.extra_transcript_slugs {
        if !slugs.contains(s) {
            slugs.push(s.clone());
        }
    }

    slugs.sort();
    slugs.dedup();
    eprintln!("Resolved transcript slugs: {}", slugs.join(", "));
    Ok(slugs)
}

fn git_worktree_paths(project_root: &Path) -> Result<Vec<PathBuf>> {
    let output = Command::new("git")
        .args(["worktree", "list", "--porcelain"])
        .current_dir(project_root)
        .output()
        .context("git worktree list")?;

    if !output.status.success() {
        anyhow::bail!(
            "git worktree list failed: {}",
            String::from_utf8_lossy(&output.stderr)
        );
    }

    let mut paths = Vec::new();
    let text = String::from_utf8_lossy(&output.stdout);
    for line in text.lines() {
        if let Some(path) = line.strip_prefix("worktree ") {
            paths.push(PathBuf::from(path));
        }
    }
    Ok(paths)
}

pub fn discover_segments(slugs: &[String]) -> Result<Vec<TranscriptSegment>> {
    let projects = cursor_projects_dir();
    let mut segments = Vec::new();

    for slug in slugs {
        let root = projects.join(slug).join("agent-transcripts");
        if !root.is_dir() {
            continue;
        }

        for entry in walkdir::WalkDir::new(&root)
            .follow_links(false)
            .into_iter()
            .filter_map(|e| e.ok())
        {
            let path = entry.path();
            if !path.is_file() {
                continue;
            }
            if path.extension().and_then(|e| e.to_str()) != Some("jsonl") {
                continue;
            }

            let transcript_id = session_id_from_path(&root, path)?;
            let relative_path = path
                .strip_prefix(&root)
                .context("strip agent-transcripts prefix")?
                .to_string_lossy()
                .replace('\\', "/");

            let mtime = std::fs::metadata(path)
                .and_then(|m| m.modified())
                .unwrap_or(SystemTime::UNIX_EPOCH);

            segments.push(TranscriptSegment {
                transcript_id,
                relative_path,
                absolute_path: path.to_path_buf(),
                mtime,
            });
        }
    }

    segments.sort_by_key(|s| s.mtime);
    Ok(segments)
}

fn session_id_from_path(agent_transcripts: &Path, jsonl: &Path) -> Result<String> {
    let rel = jsonl
        .strip_prefix(agent_transcripts)
        .context("relative to agent-transcripts")?;
    let parts: Vec<_> = rel.components().collect();
    match parts.first() {
        Some(std::path::Component::Normal(id)) => Ok(id.to_string_lossy().into_owned()),
        _ => anyhow::bail!("unexpected jsonl path: {}", jsonl.display()),
    }
}
