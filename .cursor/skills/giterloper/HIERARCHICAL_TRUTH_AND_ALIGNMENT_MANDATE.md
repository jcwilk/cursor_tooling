# Hierarchical truth and alignment (giterloper knowledge)

This document defines how **layers of truth** relate when using **giterloper** as a versioned knowledge store: universal instructions at the project root, **human-authored normative knowledge** in the giterloper corpus (markdown under `knowledge/`, versioned by Git commits and **pins**), **regression testing** (executable alignment), **implementation**, and **operational notes** (deployment, narrative, non-contract docs). It complements—not replaces—root agent guidance such as `AGENTS.md`.

---

## Why this hierarchy exists

**Human bandwidth:** Automated agents can produce far more code and churn than a maintainer can review line by line. **Normative knowledge in giterloper** is the **narrow, human-edited control surface**: the maintainer steers **intent** there; agents align **tests** and **implementation** beneath that layer.

**Drift:** Small divergences at the code or test layer are inevitable. Without a **single high-precedence** product contract that stays short enough to own, those divergences **accumulate**. The hierarchy makes **intent** visible at the top so **repair** has a clear target.

This document states **order**, **repair direction**, and **scope rules** for those layers.

---

## 1. Orthogonality: root instructions vs knowledge slices

**Root instruction files** (for example `AGENTS.md`, `CONVENTIONS.md`, and similar top-level guidance) govern **universal** agent behavior, development process, and coding standards for the whole project.

**Area slices** in the giterloper knowledge store govern **product or system behavior** for that slice only. **Regression tests** pair with those slices for **executable** alignment by naming convention and documented slice boundaries (how slices defer to each other).

If these layers appear to overlap, **call the overlap out explicitly**. In general, **knowledge slices should be adjusted to conform to repo-wide root instructions**, not the other way around. **Changing root instructions** is reserved for **systemic or process change** requested by the user—not for routine product tweaks.

---

## 2. Precedence within a slice

For **behavior** in an area, when sources conflict, use this order (highest wins first):

1. **Applicable giterloper knowledge** for that slice (normative markdown at the pinned revision you are using)
2. **Regression tests** (executable checks; they do not override normative knowledge)
3. **Current implementation** (code may drift; align it upward)

**Operational and narrative docs** (deployment, vision, use-case stories) may **incidentally** describe behavior but **must not lock** it. On conflict between those documents and giterloper knowledge, tests, or intentional contracts elsewhere, **update the operational docs to conform**—do not treat them as overruling normative knowledge or tests for product truth.

**Repair (behavior):** When the applicable knowledge, tests, and implementation disagree on **behavior**, treat the knowledge as authoritative **unless** the human is **intentionally** changing the contract. **Bring implementation and tests into alignment** with the knowledge (and any paired user-visible strings or tool descriptions). Do **not** rewrite normative knowledge to match failing tests or drifting code without **explicit human direction** to change the contract.

**Conflict resolution (examples):**

- Knowledge says X, test expects Y, code does Z → align **code and tests** to the knowledge; do not change the knowledge without the user.
- Test says X, code does Y, and nothing in (1) settles it → treat the test as the intended behavior for that gap; fix **code** (or the test if it is wrong—still without contradicting (1)).
- Two markdown docs disagree → the more **authoritative / behavior-normative** source wins; if unclear, ask the user before persisting.

**Required behavior for agents:**

- If tests conflict with (1), treat the tests as **stale** relative to the contract and update them (with implementation) to restore alignment with the normative knowledge.
- If code conflicts with tests and (1), align code to (1) first, then align tests to the same contract.
- Never file or execute work that moves behavior away from (1) unless the user **explicitly** requests that contract change.

---

## 3. Alignment, divergence, and history

- **Hierarchical alignment** means **giterloper knowledge, tests, code, and tickets/commits** are **intentionally kept in sync** for a slice: the same intent is visible across layers.
- **Hierarchical divergence** is **drift**—when layers disagree without an explicit, tracked decision to change.

Agents should use **commits** (and ticket linkage where applicable) to show **joint intent** across knowledge, test, and code changes. **Do not add changelog sections inside normative knowledge files** to track evolution; **git history is the journal** for how normative text evolved. **Giterloper pins and SHAs** let you name and retrieve **prior** states of the knowledge store for comparison and epic targeting.

---

## 4. Duplication and contradictions across knowledge slices

**Duplication across knowledge documents should be minimized.** Small, intentional overlap is acceptable when it aids reading, but **overlapping claims must not contradict** one another.

**Verifier responsibility:** verification should **flag conflicting product claims between knowledge documents** where that is in scope. This is **not** a mandate to treat every root instruction file as a normative product checklist.

---

## 5. Initial rollout and regression coverage

**Strict alignment at rollout:** every **topic or behavior exercised by regression tests** for an area **must be represented** in the **matching knowledge slice** so the suite starts in **strict alignment** with written truth. A slice may use **more than one** knowledge file; together they must cover what the tests encode as product law. **Which files exist and how slices relate** should be documented for the project; **test topic trees** follow naming aligned with those slices—not necessarily a hand-maintained table in every README.

---

## 6. Ongoing rules: tests, knowledge, and scope

- If behavior is **not important enough** to mention in the knowledge slice, it **should not** get a dedicated test that encodes that behavior as contract.
- If behavior **deserves a test** as part of the product contract, it **deserves a mention** in the relevant knowledge slice.

Here **“mention”** means the knowledge should record the **contract-relevant behavior or theme** (what a maintainer would need to know to steer the product)—**not** a mirror of every test case name, assertion, or scenario list. Judgement applies: the knowledge is **not** a prose index of the suite; avoid **padding** to echo tests one-for-one.

**Knowledge edits MUST only be made when tied to the current user or task scope.** No **drive-by** knowledge edits unrelated to the work at hand.

---

## 7. Size and growth of knowledge slices

Target roughly **two pages** of comfortable **human skim** per knowledge **file** for a slice. If a topic domain **outgrows** that, prefer **splitting into additional files** (and matching test organization when the task warrants expansion) rather than unbounded growth of a single file.

---

## Summary

| Layer | Role |
|--------|------|
| Root instructions (`AGENTS.md`, `CONVENTIONS.md`, …) | Universal process and standards |
| **Giterloper knowledge** (`knowledge/**/*.md` at a chosen pin/SHA) | **Human-authored** normative behavior per slice—the **control surface** agents align to; keep it lean |
| Regression tests | Executable checks; below normative knowledge for product truth |
| Code | Lowest; implement knowledge and passing tests |
| Operational / narrative docs | Deployment, **non-locking** narrative; must not define product law |

Together, these rules keep **hierarchical alignment** explicit and **divergence** visible and correctable. **Pins and commit SHAs** tie epics and tickets to **specific knowledge states**—baseline vs target—without conflating “current repo checkout” with “the contract this work is driving toward.”
