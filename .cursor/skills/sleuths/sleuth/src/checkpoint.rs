use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub struct SegmentKey {
    pub transcript_id: String,
    pub relative_path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Checkpoint {
    #[serde(default)]
    pub processed: Vec<ProcessedSegment>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessedSegment {
    pub transcript_id: String,
    pub relative_path: String,
    pub line_count: u64,
}

impl Checkpoint {
    pub fn load(path: &Path) -> Result<Self> {
        if !path.exists() {
            return Ok(Self::default());
        }
        let raw = std::fs::read_to_string(path)
            .with_context(|| format!("read checkpoint {}", path.display()))?;
        Ok(serde_yaml::from_str(&raw)?)
    }

    pub fn save(&self, path: &Path) -> Result<()> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        let raw = serde_yaml::to_string(self)?;
        std::fs::write(path, raw)?;
        Ok(())
    }

    pub fn line_count_map(&self) -> HashMap<SegmentKey, u64> {
        self.processed
            .iter()
            .map(|p| {
                (
                    SegmentKey {
                        transcript_id: p.transcript_id.clone(),
                        relative_path: p.relative_path.clone(),
                    },
                    p.line_count,
                )
            })
            .collect()
    }

    pub fn upsert_segment(&mut self, key: SegmentKey, line_count: u64) {
        if let Some(existing) = self.processed.iter_mut().find(|p| {
            p.transcript_id == key.transcript_id && p.relative_path == key.relative_path
        }) {
            existing.line_count = line_count;
        } else {
            self.processed.push(ProcessedSegment {
                transcript_id: key.transcript_id,
                relative_path: key.relative_path,
                line_count,
            });
        }
    }
}

pub fn checkpoint_path(sleuth_dir: &Path) -> PathBuf {
    sleuth_dir.join("checkpoint.yaml")
}
