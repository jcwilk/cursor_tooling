use crate::config::sleuths_dir;
use anyhow::{Context, Result};
use std::path::Path;

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
