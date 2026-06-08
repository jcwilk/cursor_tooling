use crate::config::{InferenceApi, OllamaConfig};
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicU64, Ordering};
use std::time::Duration;

static INFERENCE_CALLS: AtomicU64 = AtomicU64::new(0);

pub fn inference_call_count() -> u64 {
    INFERENCE_CALLS.load(Ordering::Relaxed)
}

pub fn reset_inference_call_count() {
    INFERENCE_CALLS.store(0, Ordering::Relaxed);
}

#[derive(Serialize)]
struct OllamaGenerateRequest {
    model: String,
    prompt: String,
    stream: bool,
}

#[derive(Deserialize)]
struct OllamaGenerateResponse {
    response: String,
}

#[derive(Serialize)]
struct ChatMessage<'a> {
    role: &'a str,
    content: &'a str,
}

#[derive(Serialize)]
struct OpenAiChatRequest<'a> {
    model: String,
    messages: Vec<ChatMessage<'a>>,
    stream: bool,
}

#[derive(Deserialize)]
struct OpenAiChatResponse {
    choices: Vec<OpenAiChatChoice>,
}

#[derive(Deserialize)]
struct OpenAiChatChoice {
    message: OpenAiChatMessage,
}

#[derive(Deserialize)]
struct OpenAiChatMessage {
    content: Option<String>,
}

pub struct InferenceClient {
    config: OllamaConfig,
}

impl InferenceClient {
    pub fn new(config: OllamaConfig) -> Result<Self> {
        Ok(Self { config })
    }

    pub fn generate(&self, prompt: &str) -> Result<String> {
        INFERENCE_CALLS.fetch_add(1, Ordering::Relaxed);
        match self.config.api {
            InferenceApi::Ollama => self.generate_ollama(prompt),
            InferenceApi::OpenAiChat => self.generate_openai_chat(prompt),
        }
    }

    fn generate_ollama(&self, prompt: &str) -> Result<String> {
        let url = format!(
            "{}/api/generate",
            self.config.base_url.trim_end_matches('/')
        );
        let body = OllamaGenerateRequest {
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

        let parsed: OllamaGenerateResponse = resp.into_json().context("parse Ollama response")?;
        Ok(parsed.response.trim().to_string())
    }

    fn generate_openai_chat(&self, prompt: &str) -> Result<String> {
        let url = format!(
            "{}/v1/chat/completions",
            self.config.base_url.trim_end_matches('/')
        );
        let body = OpenAiChatRequest {
            model: self.config.model.clone(),
            messages: vec![ChatMessage {
                role: "user",
                content: prompt,
            }],
            stream: false,
        };

        let resp = ureq::post(&url)
            .timeout(Duration::from_secs(600))
            .send_json(serde_json::to_value(&body)?)
            .with_context(|| format!("POST {url}"))?;

        let status = resp.status();
        let body_text = resp.into_string().unwrap_or_default();
        if !(200..300).contains(&status) {
            anyhow::bail!(
                "OpenAI chat request failed ({status}) at {url}: {body_text}"
            );
        }

        parse_openai_chat_response(&body_text)
    }
}

fn parse_openai_chat_response(body: &str) -> Result<String> {
    let parsed: OpenAiChatResponse =
        serde_json::from_str(body).context("parse OpenAI chat response")?;
    let content = parsed
        .choices
        .first()
        .and_then(|c| c.message.content.as_deref())
        .unwrap_or("")
        .trim()
        .to_string();
    Ok(content)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_openai_chat_extracts_assistant_content() {
        let body = r#"{
            "choices": [{
                "message": { "role": "assistant", "content": "hello" }
            }]
        }"#;
        assert_eq!(parse_openai_chat_response(body).unwrap(), "hello");
    }

    #[test]
    fn parse_openai_chat_trims_whitespace() {
        let body = r#"{
            "choices": [{
                "message": { "role": "assistant", "content": "  connected  " }
            }]
        }"#;
        assert_eq!(parse_openai_chat_response(body).unwrap(), "connected");
    }

    #[test]
    fn parse_openai_chat_empty_choices() {
        let body = r#"{ "choices": [] }"#;
        assert_eq!(parse_openai_chat_response(body).unwrap(), "");
    }
}
