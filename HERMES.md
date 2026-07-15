# HERMES.md

This repository follows the documentation-first workflow from [HappyMonkeyAI/AgentsProtocol](https://github.com/HappyMonkeyAI/AgentsProtocol).

## Operating Rules

- Start each session by reading `README.md`, `CONTEXT.md`, `AGENTS.md`, and relevant `.agent/memories/` entries.
- Query memory by task-relevant tags before implementation.
- Batch safe read-only context gathering.
- Map the blast radius before non-trivial edits.
- Keep changes surgical and aligned with the MVP.
- Verify before declaring work complete.
- Update memory when decisions or reusable lessons are created.
- Avoid speculative integrations before the core demo loop works.

## Ratchet Protocol

Use small verified increments:

1. Make a focused change.
2. Run the relevant check.
3. Update docs or memory if behavior changed.
4. Commit only when the increment is coherent, verified, and committing is authorized.

## Memory Maintenance

- Store facts and architecture in `codebase_insights/` or `architectural_decisions/`.
- Store dated plans and outcomes in `history/`.
- Store reusable workflows and lessons in `patterns_and_lessons.md`.
- Periodically audit memory against the current code and archive stale guidance.

## Stop Conditions

Stop and replan if:

- The task needs more than three corrective passes.
- The implementation expands beyond the MVP without a clear demo payoff.
- Generated documentation cannot cite timestamps, frames, or transcript spans.
