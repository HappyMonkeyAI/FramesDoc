# Video Document Agent

Video Document Agent turns team meeting recordings into timestamped internal documentation. It targets meetings where important knowledge appears briefly on screen: terminal commands, setup walkthroughs, product demos, incident-review steps, and decisions that people later need to find again.

## Hackathon Pitch

An AI documentation agent that watches meeting recordings, finds the important on-screen moments, and turns them into linked runbooks and knowledge pages.

## Status

Protocol and project-planning bootstrap only. Application code has not been implemented yet, so there is no runnable quickstart.

## MVP Scope

The first demo should prove one narrow workflow:

1. Upload or point to one MP4 meeting recording.
2. Generate or ingest a timestamped transcript.
3. Extract representative keyframes.
4. Run OCR or vision analysis on candidate frames.
5. Use an OpenAI model to classify documentation-worthy moments.
6. Generate markdown or HTML with screenshots, transcript context, extracted commands, and timestamps back to the video.

## Target Output

The generated page should include:

- Sections such as setup, commands shown, warnings, decisions, and workflow steps
- Screenshots for key visual moments
- Extracted visible text or command snippets
- Transcript-backed summaries
- Timestamp links or timestamp references

## Non-Goals For The First Slice

- Full enterprise video ingestion
- Perfect Confluence synchronization
- Permission and identity management
- Long-term semantic search across many recordings
- Polished team administration features

## Project Docs

- `20260715-planning.txt` is the source planning conversation.
- `CONTEXT.md` captures current architecture and constraints.
- `AGENTS.md` contains project-specific agent rules.
- `HERMES.md` records the local Agents Protocol operating loop.
- `.agent/memories/` stores long-term memory for future agents.
- `docs/adr/` stores architecture decision records.
- `research/` stores external references and notes.
