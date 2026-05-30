use crate::config::OllamaConfig;
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::time::Duration;

#[derive(Serialize)]
struct GenerateRequest {
    model: String,
    prompt: String,
    stream: bool,
}

#[derive(Deserialize)]
struct GenerateResponse {
    response: String,
}

pub struct OllamaClient {
    config: OllamaConfig,
}

impl OllamaClient {
    pub fn new(config: OllamaConfig) -> Result<Self> {
        Ok(Self { config })
    }

    pub fn generate(&self, prompt: &str) -> Result<String> {
        let url = format!(
            "{}/api/generate",
            self.config.base_url.trim_end_matches('/')
        );
        let body = GenerateRequest {
            model: self.config.model.clone(),
            prompt: prompt.to_string(),
            stream: false,
        };

        let resp = ureq::post(&url)
            .timeout(Duration::from_secs(600))
            .send_json(serde_json::to_value(&body)?)
            .with_context(|| format!("POST {url}"))?;

        let status = resp.status();
        if !(200..300).contains(&status) {
            anyhow::bail!(
                "Ollama request failed ({status}): {}",
                resp.into_string().unwrap_or_default()
            );
        }

        let parsed: GenerateResponse = resp.into_json().context("parse Ollama response")?;
        Ok(parsed.response.trim().to_string())
    }
}

pub fn map_prompt(sleuth_prompt: &str, chunk: &str, session_tag: &str) -> String {
    format!(
        r#"You are extracting information from Cursor agent conversation transcripts for a sleuth lens.

Sleuth lens:
{sleuth_prompt}

Source session: {session_tag}

Instructions:
- Extract ONLY facts present in the source chunk that match the sleuth lens.
- If nothing relevant, respond with exactly: NO_MATCH
- Quote file paths and identifiers verbatim from the source.
- Do not invent details.

Source chunk:
{chunk}
"#
    )
}

pub fn reduce_prompt(sleuth_prompt: &str, existing_summary: &str, map_output: &str, session_tag: &str) -> String {
    format!(
        r#"You are merging new extractions into an existing sleuth summary.

Sleuth lens:
{sleuth_prompt}

New extraction from {session_tag}:
{map_output}

Existing summary:
{existing_summary}

Instructions:
- Preserve prior bullets unless clearly superseded.
- Add new items from the extraction; dedupe lightly.
- Tag new items with the session tag provided.
- Quote file paths verbatim when present in the source.
- Use markdown bullet lists.
- If the new extraction is NO_MATCH, return the existing summary unchanged.
"#
    )
}
