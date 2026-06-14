mod checkpoint;
mod chunk;
mod config;
mod context_budget;
mod discover;
mod inference;
mod jsonl_extract;
mod pipeline;
mod prompts;
mod query;
mod refresh;
mod relevance;
mod reset;
mod slug;
mod token;
mod verbose;

use anyhow::Result;
use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "sleuth", about = "Incremental summarization of Cursor agent transcripts")]
struct Cli {
    /// Project root (directory containing `.sleuths/`)
    #[arg(long, global = true, default_value = ".")]
    project_root: PathBuf,

    /// Log per-segment and per-inference progress to stderr
    #[arg(long, global = true)]
    verbose: bool,

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
    /// Remove summary and checkpoint so the next refresh starts from scratch
    Reset {
        /// Sleuth id (matches `.sleuths/queries/<id>.yaml`)
        #[arg(long)]
        sleuth: Option<String>,

        /// Reset every sleuth under `.sleuths/queries/`
        #[arg(long)]
        all: bool,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    verbose::set_verbose(cli.verbose);
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
        Commands::Reset { sleuth, all } => {
            if all {
                reset::reset_all(&project_root)?;
            } else if let Some(id) = sleuth {
                reset::reset_sleuth(&project_root, &id)?;
            } else {
                anyhow::bail!("specify --sleuth <id> or --all");
            }
        }
    }

    Ok(())
}
