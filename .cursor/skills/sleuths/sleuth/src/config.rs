use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SleuthsConfig {
    pub ollama: OllamaConfig,
    #[serde(default)]
    pub transcripts: TranscriptsConfig,
    #[serde(default)]
    pub processing: ProcessingConfig,
}

fn default_context_budget() -> u64 {
    16384
}

fn default_response_headroom() -> u64 {
    1000
}

fn default_pass_summary_cap() -> u64 {
    4000
}

fn default_final_summary_target() -> u64 {
    4000
}

fn default_chunk_lines() -> u64 {
    1
}

fn default_max_chunks_per_batch() -> u64 {
    20
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessingConfig {
    #[serde(default = "default_context_budget")]
    pub context_budget_tokens: u64,
    #[serde(default = "default_response_headroom")]
    pub response_headroom_tokens: u64,
    #[serde(default = "default_pass_summary_cap")]
    pub pass_summary_cap_tokens: u64,
    #[serde(default = "default_final_summary_target")]
    pub final_summary_target_tokens: u64,
    #[serde(default = "default_chunk_lines")]
    pub chunk_lines: u64,
    #[serde(default = "default_max_chunks_per_batch")]
    pub max_chunks_per_batch: u64,
}

impl Default for ProcessingConfig {
    fn default() -> Self {
        Self {
            context_budget_tokens: default_context_budget(),
            response_headroom_tokens: default_response_headroom(),
            pass_summary_cap_tokens: default_pass_summary_cap(),
            final_summary_target_tokens: default_final_summary_target(),
            chunk_lines: default_chunk_lines(),
            max_chunks_per_batch: default_max_chunks_per_batch(),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, Default)]
#[serde(rename_all = "kebab-case")]
pub enum InferenceApi {
    #[default]
    Ollama,
    #[serde(alias = "llama-cpp", alias = "llama.cpp", alias = "openai", alias = "chat-completions")]
    OpenAiChat,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OllamaConfig {
    pub base_url: String,
    pub model: String,
    #[serde(default)]
    pub api: InferenceApi,
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
             inference endpoint (Ollama or llama.cpp OpenAI chat). Sleuth does not start a local \
             daemon; refresh only HTTP-calls the URL you configure (file is gitignored)",
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn inference_api_defaults_to_ollama() {
        let raw = r#"
ollama:
  base_url: http://127.0.0.1:11434
  model: test
"#;
        let cfg: SleuthsConfig = serde_yaml::from_str(raw).unwrap();
        assert_eq!(cfg.ollama.api, InferenceApi::Ollama);
    }

    #[test]
    fn inference_api_parses_llama_cpp_alias() {
        let raw = r#"
ollama:
  base_url: http://192.168.1.110:11435
  model: fast-text-qwen3-8b
  api: llama-cpp
"#;
        let cfg: SleuthsConfig = serde_yaml::from_str(raw).unwrap();
        assert_eq!(cfg.ollama.api, InferenceApi::OpenAiChat);
    }

    #[test]
    fn processing_defaults() {
        let cfg = ProcessingConfig::default();
        assert_eq!(cfg.chunk_lines, 1);
        assert_eq!(cfg.max_chunks_per_batch, 20);
        assert_eq!(cfg.context_budget_tokens, 16384);
        assert_eq!(cfg.response_headroom_tokens, 1000);
    }
}

pub fn cursor_projects_dir() -> PathBuf {
    dirs_home().join(".cursor").join("projects")
}

fn dirs_home() -> PathBuf {
    std::env::var("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from("/home/user"))
}
