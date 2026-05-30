use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SleuthsConfig {
    pub ollama: OllamaConfig,
    #[serde(default)]
    pub transcripts: TranscriptsConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OllamaConfig {
    pub base_url: String,
    pub model: String,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub struct TranscriptsConfig {
    #[serde(default)]
    pub extra_transcript_slugs: Vec<String>,
}

pub fn sleuths_dir(project_root: &Path) -> PathBuf {
    project_root.join(".sleuths")
}

pub fn config_path(project_root: &Path) -> PathBuf {
    sleuths_dir(project_root).join("config.yaml")
}

pub fn ensure_sleuths_dirs(project_root: &Path) -> Result<()> {
    let dir = sleuths_dir(project_root);
    std::fs::create_dir_all(dir.join("queries"))?;
    Ok(())
}

pub fn load_config(project_root: &Path) -> Result<SleuthsConfig> {
    ensure_sleuths_dirs(project_root)?;

    let path = config_path(project_root);
    if !path.exists() {
        bail!(
            "missing {} — create it with ollama.base_url and ollama.model pointing at your \
             Ollama-compatible inference endpoint (remote or LAN). Sleuth does not start Ollama \
             locally; refresh only HTTP-calls the URL you configure (file is gitignored)",
            path.display()
        );
    }

    let raw = std::fs::read_to_string(&path)
        .with_context(|| format!("read {}", path.display()))?;
    let cfg: SleuthsConfig = serde_yaml::from_str(&raw)
        .with_context(|| format!("parse {}", path.display()))?;

    if cfg.ollama.base_url.trim().is_empty() || cfg.ollama.model.trim().is_empty() {
        bail!(
            "{} must set non-empty ollama.base_url and ollama.model",
            path.display()
        );
    }

    Ok(cfg)
}

pub fn cursor_projects_dir() -> PathBuf {
    dirs_home().join(".cursor").join("projects")
}

fn dirs_home() -> PathBuf {
    std::env::var("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from("/home/user"))
}
