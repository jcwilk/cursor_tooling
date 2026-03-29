# Hierarchical truth and alignment (giterloper knowledge)

How layers of truth relate when using giterloper as a versioned knowledge store. Complements—not replaces—root agent guidance (`AGENTS.md`, etc.).

## Layer precedence (highest wins)

| Layer | Role |
|-------|------|
| Root instructions (`AGENTS.md`, `CONVENTIONS.md`, …) | Universal process and standards for the whole project |
| **Giterloper knowledge** (`knowledge/**/*.md` at a pin/SHA) | Human-authored normative behavior per slice — the control surface agents align to |
| Regression tests | Executable checks; below normative knowledge for product truth |
| Code / implementation | Lowest; implement knowledge and pass tests |
| Operational / narrative docs | Deployment, vision, non-locking narrative; **never** defines product law |

**Why this hierarchy exists.** Automated agents can produce far more code and test churn than a maintainer can review line-by-line. The giterloper knowledge layer exists to be a **deliberately narrow control surface** — short enough that a human can actually own and review it. The maintainer steers *intent* there; agents align tests and implementation beneath it. Without that single, high-precedence contract layer, small divergences at the code or test level accumulate into drift with no clear repair target.

## Conflict resolution

When sources disagree on behavior, **repair downward** — align lower layers to higher ones:

- Knowledge says X, test expects Y, code does Z → fix tests and code to match knowledge.
- Test says X, code does Y, knowledge is silent → treat the test as intended; fix code.
- Two knowledge docs disagree → the more authoritative/behavior-normative source wins; if unclear, ask the user.

**Never** rewrite normative knowledge to match failing tests or drifting code without **explicit human direction** to change the contract.

## Root instructions vs knowledge slices

Root instructions govern universal process and standards. Knowledge slices govern product/system behavior for their area only. When they appear to overlap, call it out explicitly. **Knowledge slices conform to root instructions**, not the reverse. Changing root instructions is reserved for systemic/process changes requested by the user.

## Keeping layers in sync

- Use commits (and ticket linkage) to show joint intent across knowledge, test, and code changes.
- **Do not** add changelog sections inside knowledge files — git history is the journal. Pins and SHAs let you reference prior states for comparison and epic targeting.
- Minimize duplication across knowledge slices. Small overlap for readability is fine, but overlapping claims **must not contradict**.
- Verifiers should flag conflicting product claims between knowledge docs where in scope.

## Tests ↔ knowledge parity

- Every behavior exercised by regression tests **must be represented** in the matching knowledge slice (strict alignment at rollout).
- If behavior deserves a test, it deserves a mention in knowledge. If it's not worth mentioning in knowledge, it shouldn't get a contract-level test.
- "Mention" means recording the contract-relevant theme — **not** mirroring every test case or assertion. Knowledge is not a prose index of the suite.

## Scope and size

- **Knowledge edits must be tied to the current task scope.** No drive-by edits.
- Target roughly **two pages of human skim** per knowledge file. If a slice outgrows that, split into additional files (with matching test organization) rather than letting one file grow unbounded.
