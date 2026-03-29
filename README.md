# Cursor tooling (reference boilerplate)

This repository is a **reference boilerplate** for Cursor-focused workflows: agents, skills, ticket tracking, and small automation hooks you can copy, adapt, or **symlink into a user-wide Cursor config** so the same patterns work across many projects.

## What it is for

- **Symlink source for global tooling** — Point `~/.cursor/skills/`, `~/.cursor/agents/`, or individual files at copies or symlinks of the contents here (or a fork) so one maintained tree backs every workspace. Keep secrets in each project’s **`.env`** (see **`.env.example`**); this repo’s **`.gitignore`** excludes **`.env`**.
- **Research and automation** — Use it as a sandbox for MCP setup (e.g. **`.cursor/mcp.json`** patterns), scripted flows (**`./tk`** for tickets), and experiments with Cursor’s Task tool and subagents without mixing them into an application codebase.
- **Designing new agents and skills** — **`.cursor/agents/`** holds Task-oriented subagent definitions; **`.cursor/skills/`** holds short, repeatable workflows for the main chat agent. Iterate here, then promote stable pieces to your user-wide **`~/.cursor/`** tree or into other repos.

## What’s in the box

| Area | Role |
|------|------|
| **`.cursor/skills/`** | Workflow skills (`SKILL.md` files) the primary agent can follow. |
| **`.cursor/agents/`** | Definitions meant to run **inside Cursor’s Task tool**, not as pasted step lists. |
| **`scripts/ticket` + `./tk`** | Vendored [wedow/ticket](https://github.com/wedow/ticket) CLI — markdown tickets under **`.tickets/`** (optional **`TICKETS_DIR`** in **`.env`**). |

## MCP (`giterloper`)

**`.cursor/mcp.json`** in this boilerplate is only an example. **You must edit it** so the **giterloper** server points at **your** install (e.g. adjust `cwd` and any script paths), **or** configure it to use a **hosted / cloud URL** for giterloper if that’s how you run it, **or delete the file** (or remove the `giterloper` entry) if you do not use that MCP server. Until you do, paths will not match your machine.

## Docs in this repo

- **[AGENTS.md](./AGENTS.md)** — Ticket CLI usage, skills vs agents, git branch expectations, environment.
- **[CONVENTIONS.md](./CONVENTIONS.md)** — Project coding conventions (fill in as you extend the boilerplate).

## Quick start

```bash
./tk help          # ticket commands (after .tickets exists or TICKETS_DIR is set)
cp .env.example .env   # then add any API keys optional agents need
```

Clone or fork this repo, customize, and wire it into **`~/.cursor/`** however fits your setup—this tree is meant to stay small, readable, and easy to reuse.
