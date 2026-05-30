mod checkpoint;
mod config;
mod discover;
mod jsonl_extract;
mod ollama;
mod refresh;
mod slug;

use anyhow::Result;
use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "sleuth", about = "Incremental summarization of Cursor agent transcripts")]
struct Cli {
    /// Project root (directory containing `.sleuths/`)
    #[arg(long, global = true, default_value = ".")]
    project_root: PathBuf,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Incrementally refresh sleuth summaries
    Refresh {
        /// Sleuth id (matches `.sleuths/queries/<id>.yaml`)
        #[arg(long)]
        sleuth: Option<String>,

        /// Refresh every sleuth under `.sleuths/queries/`
        #[arg(long)]
        all: bool,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let project_root = cli.project_root.canonicalize()?;

    match cli.command {
        Commands::Refresh { sleuth, all } => {
            if all {
                refresh::refresh_all(&project_root)?;
            } else if let Some(id) = sleuth {
                refresh::refresh_sleuth(&project_root, &id)?;
            } else {
                anyhow::bail!("specify --sleuth <id> or --all");
            }
        }
    }

    Ok(())
}
