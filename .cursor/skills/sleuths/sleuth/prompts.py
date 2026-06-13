from __future__ import annotations

from sleuth.config import ProcessingConfig
from sleuth.query import SleuthQuery
from sleuth.token import estimate_tokens


def relevance_prompt(
    query: SleuthQuery,
    indexed_chunks: list[tuple[int, str]],
    session_tag: str,
) -> str:
    body = ""
    for idx, text in indexed_chunks:
        body += f"\n--- chunk {idx} ---\n{text}\n"
    return f"""You are filtering Cursor agent transcript chunks for relevance to a sleuth lens.

Sleuth topic: {query.description}

Lens instructions:
{query.prompt}

Source session: {session_tag}

Each chunk below is labeled with a zero-based index. Respond with ONLY a JSON object (no prose, no markdown fences) listing indices of chunks whose content is relevant to the sleuth topic:

{{"relevant_ids": [0, 2]}}

If nothing is relevant, respond: {{"relevant_ids": []}}

Indexed chunks:{body}
"""


def summarize_prompt(
    query: SleuthQuery,
    indexed_chunks: list[tuple[int, str]],
    session_tag: str,
    pass_cap_tokens: int,
) -> str:
    body = ""
    for idx, text in indexed_chunks:
        body += f"\n--- chunk {idx} ---\n{text}\n"
    return f"""You are summarizing relevant Cursor agent transcript chunks for a sleuth lens.

Sleuth topic: {query.description}

Lens instructions:
{query.prompt}

Source session: {session_tag}

Produce a markdown bullet summary of facts present in the chunks that match the lens.
Keep the summary under approximately {pass_cap_tokens} tokens.
Quote file paths and identifiers verbatim. Do not invent details.

Relevant chunks:{body}
"""


def merge_prompt(
    query: SleuthQuery,
    summaries: list[str],
    session_tag: str,
    target_cap_tokens: int,
    seed_aggregate: str | None = None,
) -> str:
    body = ""
    for i, s in enumerate(summaries):
        body += f"\n--- summary {i} ---\n{s}\n"
    seed_section = ""
    if seed_aggregate and seed_aggregate.strip():
        seed_section = f"""
Prior aggregate summary (use as the starting merged document; deduplicate against new material):
{seed_aggregate}
"""
    return f"""You are merging sleuth summaries into one consolidated document.

Sleuth topic: {query.description}

Lens instructions:
{query.prompt}

Source session: {session_tag}
{seed_section}
Summaries to merge:{body}

Instructions:
- Deduplicate overlapping facts; prefer one clear bullet per fact.
- Preserve concrete file paths and identifiers from sources.
- Use markdown bullet lists.
- Keep the merged result under approximately {target_cap_tokens} tokens.
"""


def relevance_prompt_overhead(query: SleuthQuery, session_tag: str) -> int:
    return estimate_tokens(relevance_prompt(query, [], session_tag))


def summarize_prompt_overhead(
    query: SleuthQuery,
    session_tag: str,
    pass_cap_tokens: int,
) -> int:
    return estimate_tokens(summarize_prompt(query, [], session_tag, pass_cap_tokens))


def merge_prompt_overhead(
    query: SleuthQuery,
    session_tag: str,
    target_cap_tokens: int,
    has_seed: bool,
) -> int:
    seed = "" if has_seed else None
    return estimate_tokens(merge_prompt(query, [], session_tag, target_cap_tokens, seed))


def content_budget(processing: ProcessingConfig, prompt_overhead: int) -> int:
    return max(
        0,
        processing.context_budget_tokens
        - processing.response_headroom_tokens
        - prompt_overhead,
    )
