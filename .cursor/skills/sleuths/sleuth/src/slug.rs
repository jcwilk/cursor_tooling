use std::path::Path;

/// Derive Cursor's `~/.cursor/projects/<slug>/` identifier from a workspace path.
///
/// Observed rules (see design.md):
/// - `/home/user/workspace/foo_bar` → `home-user-workspace-foo-bar`
/// - `/home/user/.cursor/worktrees/<repo>/<id>` → `home-user-cursor-worktrees-<repo>-<id>`
pub fn slug_from_path(path: &Path) -> String {
    let path = path.canonicalize().unwrap_or_else(|_| path.to_path_buf());
    let s = path.to_string_lossy();

    if let Some(rest) = s.strip_prefix("/home/user/.cursor/worktrees/") {
        let parts: Vec<&str> = rest.split('/').collect();
        if parts.len() >= 2 {
            let repo = parts[0].replace('_', "-");
            let id = parts[1];
            return format!("home-user-cursor-worktrees-{repo}-{id}");
        }
    }

    let rest = if let Some(r) = s.strip_prefix("/home/user/") {
        r
    } else {
        s.trim_start_matches('/')
    };

    let normalized = rest.replace('_', "-").replace('/', "-");
    format!("home-user-{normalized}")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn workspace_slug() {
        assert_eq!(
            slug_from_path(Path::new("/home/user/workspace/cursor_tooling")),
            "home-user-workspace-cursor-tooling"
        );
    }

    #[test]
    fn worktree_slug() {
        assert_eq!(
            slug_from_path(Path::new("/home/user/.cursor/worktrees/home_ai/bufb")),
            "home-user-cursor-worktrees-home-ai-bufb"
        );
    }
}
