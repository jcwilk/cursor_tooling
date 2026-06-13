use crate::checkpoint::checkpoint_path;
use crate::config::sleuths_dir;
use crate::query::{list_sleuth_ids, load_query};
use anyhow::Result;
use std::path::Path;

pub fn reset_sleuth(project_root: &Path, sleuth_id: &str) -> Result<()> {
    load_query(project_root, sleuth_id)?;
    reset_sleuth_artifacts(project_root, sleuth_id)
}

pub fn reset_all(project_root: &Path) -> Result<()> {
    let ids = list_sleuth_ids(project_root)?;
    if ids.is_empty() {
        anyhow::bail!("no sleuths found under .sleuths/queries/");
    }
    for id in ids {
        reset_sleuth_artifacts(project_root, &id)?;
    }
    Ok(())
}

fn reset_sleuth_artifacts(project_root: &Path, sleuth_id: &str) -> Result<()> {
    let sleuth_dir = sleuths_dir(project_root).join(sleuth_id);
    let summary_path = sleuth_dir.join("summary.md");
    let ckpt_path = checkpoint_path(&sleuth_dir);

    let mut removed = Vec::new();
    if summary_path.exists() {
        std::fs::remove_file(&summary_path)?;
        removed.push("summary.md");
    }
    if ckpt_path.exists() {
        std::fs::remove_file(&ckpt_path)?;
        removed.push("checkpoint.yaml");
    }

    if removed.is_empty() {
        eprintln!("Sleuth '{sleuth_id}': nothing to reset (no summary or checkpoint)");
    } else {
        eprintln!(
            "Sleuth '{sleuth_id}': removed {}",
            removed.join(", ")
        );
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::ensure_sleuths_dirs;
    use std::fs;

    fn write_query(root: &Path, id: &str) {
        ensure_sleuths_dirs(root).unwrap();
        let path = sleuths_dir(root).join("queries").join(format!("{id}.yaml"));
        fs::write(
            &path,
            format!(
                "id: {id}\ndescription: test\nprompt: |\n  extract things\n"
            ),
        )
        .unwrap();
    }

    fn write_artifacts(root: &Path, id: &str) {
        let dir = sleuths_dir(root).join(id);
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join("summary.md"), "# summary\n").unwrap();
        fs::write(dir.join("checkpoint.yaml"), "processed: []\n").unwrap();
    }

    #[test]
    fn reset_removes_summary_and_checkpoint() {
        let root = tempfile::tempdir().unwrap();
        write_query(root.path(), "tooling");
        write_artifacts(root.path(), "tooling");

        reset_sleuth(root.path(), "tooling").unwrap();

        let dir = sleuths_dir(root.path()).join("tooling");
        assert!(!dir.join("summary.md").exists());
        assert!(!dir.join("checkpoint.yaml").exists());
    }

    #[test]
    fn reset_is_idempotent_when_artifacts_missing() {
        let root = tempfile::tempdir().unwrap();
        write_query(root.path(), "tooling");

        reset_sleuth(root.path(), "tooling").unwrap();
        reset_sleuth(root.path(), "tooling").unwrap();
    }

    #[test]
    fn reset_all_clears_every_query_sleuth() {
        let root = tempfile::tempdir().unwrap();
        write_query(root.path(), "alpha");
        write_query(root.path(), "beta");
        write_artifacts(root.path(), "alpha");
        write_artifacts(root.path(), "beta");

        reset_all(root.path()).unwrap();

        for id in ["alpha", "beta"] {
            let dir = sleuths_dir(root.path()).join(id);
            assert!(!dir.join("summary.md").exists());
            assert!(!dir.join("checkpoint.yaml").exists());
        }
    }
}
