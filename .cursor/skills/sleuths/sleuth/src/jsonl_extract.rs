use anyhow::{Context, Result};
use serde_json::Value;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;

/// Extract text from JSONL lines `start_line_1based..=end_line` (1-based, inclusive).
pub fn extract_lines(path: &Path, start_line_1based: u64, end_line: u64) -> Result<String> {
    let file = File::open(path).with_context(|| format!("open {}", path.display()))?;
    let reader = BufReader::new(file);
    let mut parts = Vec::new();

    for (idx, line) in reader.lines().enumerate() {
        let line_no = (idx + 1) as u64;
        if line_no < start_line_1based {
            continue;
        }
        if line_no > end_line {
            break;
        }
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        let value: Value = serde_json::from_str(&line)
            .with_context(|| format!("parse jsonl line {line_no} in {}", path.display()))?;
        if let Some(text) = line_to_text(&value) {
            if !text.trim().is_empty() {
                parts.push(text);
            }
        }
    }

    Ok(parts.join("\n\n"))
}

pub fn count_lines(path: &Path) -> Result<u64> {
    let file = File::open(path)?;
    Ok(BufReader::new(file).lines().count() as u64)
}

fn line_to_text(value: &Value) -> Option<String> {
    let role = value.get("role")?.as_str()?;
    let message = value.get("message")?;
    let content = message.get("content")?.as_array()?;

    let mut blocks = Vec::new();
    for block in content {
        let kind = block.get("type")?.as_str()?;
        match kind {
            "text" => {
                if let Some(t) = block.get("text").and_then(|v| v.as_str()) {
                    blocks.push(format!("[{role}] {t}"));
                }
            }
            "tool_use" => {
                let name = block
                    .get("name")
                    .and_then(|v| v.as_str())
                    .unwrap_or("tool");
                blocks.push(format!("[{role}] tool_use: {name}"));
            }
            _ => {}
        }
    }

    if blocks.is_empty() {
        None
    } else {
        Some(blocks.join("\n"))
    }
}
