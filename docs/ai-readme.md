> ⚙ **AI Assistant Onboarding Summary**
>
> - Treat this repo as the **core pipeline** for The Talking Heads Podcast Creator.
> - The pipeline is roughly:
>   1. Ingest script/audio
>   2. Generate or ingest audio
>   3. Extract features/visemes
>   4. Construct timelines
>   5. Map to faces/avatars/assets
>   6. Export for rendering (Omniverse or other tools)
> - When modifying code:
>   - Keep each stage clear and composable.
>   - Do not mix concerns between stages (no “god scripts”).
>   - Preserve the contracts and schemas described in this document.
> - When in doubt, summarize your understanding of this document before making major changes.


# AI Readme – AI_Podcast_Creator

## Project Purpose
This repo is part of "The Talking Heads" system. Its purpose is to generate podcast-style talking head content from audio, driving visemes, animation, and related assets.

## Tech Stack (fill in more as needed)
- Language(s): (e.g., Python / TypeScript / etc.)
- Key frameworks / libs: (list main ones)
- Tools / runtimes: Omniverse, USD, Audio2Face, viseme pipelines, etc.

## Key Invariants & Constraints
- Do not break the audio → viseme → animation pipeline.
- Preserve file formats and directory structure unless explicitly told to refactor.
- Keep scripts idempotent where possible (safe to re-run).

## Coding Standards
- Match existing style in this repo.
- Add or update tests when making non-trivial changes.
- Keep functions small and cohesive when possible.
- Prefer explicit, well-named variables over cleverness.

## What You MUST NOT Do
- Do not delete or rename core pipeline entrypoints without a clear migration plan.
- Do not hardcode machine-specific absolute paths.
- Do not silently swallow exceptions; either handle them or log clearly.

## How To Work With This Repo
1. Before large changes, briefly scan:
   - `README.md` (if present)
   - `docs/architecture.md`
2. When asked to change code:
   - Identify all affected modules.
   - Propose a small plan first.
   - Then implement in small, reviewable steps.

## Notes For AI Assistants
- When you’re first loaded on this repo, summarize the architecture and key components for the human before editing.
- When in doubt, ask for clarification instead of guessing.

# AI Readme – AI_Podcast_Creator

## 1. Project Purpose

- This repo is the **AI pipeline for The Talking Heads Podcast Creator**.
- High-level goal: Generate talking-head / podcast-style video from input audio and script.
- This project focuses on:
  - Audio → features (visemes, timing)
  - Asset selection / creation (faces, backgrounds)
  - Timeline construction
  - Export-ready compositions for downstream tools (e.g., Omniverse / video renderers)

## 2. Architectural Boundaries

- This repo is **pipeline + orchestration**, not a general-purpose ML playground.
- It assumes data and models from related repos (e.g., SadTalker, DECA, 3DDFA, Omniverse tooling).
- Do **not**:
  - Hard-code absolute Windows paths.
  - Mix responsibilities of Exponis EMR or other business systems into this codebase.
  - Introduce heavy, slow dependencies without a clear need and note in `docs/architecture.md`.

## 3. Coding & Design Conventions

- Languages / stack:
  - Python (3.x) for orchestration, data processing, and ML integration.
  - CLI / scripts should be idempotent and composable.
- Conventions:
  - Prefer small, focused functions and modules.
  - Use clear, descriptive names for stages (e.g., `extract_visemes`, `build_timeline`).
  - Keep side effects (disk I/O, network calls) near the edges of the pipeline.
- Tests:
  - Unit tests live under `tests/` (or `*_test.py` near source).
  - When creating new functionality, add at least a smoke test.

## 4. Data, Assets, and Paths

- Input data: audio files (WAV/MP3), scripts, metadata in `data/` or configured paths.
- Intermediate outputs: features, viseme JSON, timelines, logs.
- Fina

# AI Readme – AI_Podcast_Creator

## 1. Project Purpose

- This repo is the **AI pipeline for The Talking Heads Podcast Creator**.
- High-level goal: Generate talking-head / podcast-style video from input audio and script.
- This project focuses on:
  - Audio → features (visemes, timing)
  - Asset selection / creation (faces, backgrounds)
  - Timeline construction
  - Export-ready compositions for downstream tools (e.g., Omniverse / video renderers)

## 2. Architectural Boundaries

- This repo is **pipeline + orchestration**, not a general-purpose ML playground.
- It assumes data and models from related repos (e.g., SadTalker, DECA, 3DDFA, Omniverse tooling).
- Do **not**:
  - Hard-code absolute Windows paths.
  - Mix responsibilities of Exponis EMR or other business systems into this codebase.
  - Introduce heavy, slow dependencies without a clear need and note in `docs/architecture.md`.

## 3. Coding & Design Conventions

- Languages / stack:
  - Python (3.x) for orchestration, data processing, and ML integration.
  - CLI / scripts should be idempotent and composable.
- Conventions:
  - Prefer small, focused functions and modules.
  - Use clear, descriptive names for stages (e.g., `extract_visemes`, `build_timeline`).
  - Keep side effects (disk I/O, network calls) near the edges of the pipeline.
- Tests:
  - Unit tests live under `tests/` (or `*_test.py` near source).
  - When creating new functionality, add at least a smoke test.

## 4. Data, Assets, and Paths

- Input data: audio files (WAV/MP3), scripts, metadata in `data/` or configured paths.
- Intermediate outputs: features, viseme JSON, timelines, logs.
- Final outputs: ready-to-render bundles (e.g., audio, viseme JSON, config for Omniverse or other renderer).
- **Never**:
  - Hard-code user-specific paths (`/mnt/c/Users/...`, `D:\dev\...`).
  - Assume a specific machine layout; use configs or environment variables.

## 5. Logging, Errors, and Observability

- Logging:
  - Prefer structured logs where possible (stage, file, status).
  - Do not log full raw audio blobs; log only references and metadata.
- Errors:
  - Fail early with clear error messages that mention which pipeline stage failed.
  - When catching exceptions, either:
    - Re-raise with more context, or
    - Return a structured error result that upstream stages can handle.

## 6. Things You Must Not Break

- End-to-end pipeline steps:
  1. Script ingestion
  2. TTS / audio generation (if applicable)
  3. Feature extraction (visemes, phonemes, timing)
  4. Timeline construction
  5. Asset selection / mapping
  6. Composition/export interface

- Existing CLI entrypoints and key config files.
- Any agreed-on output schema used by downstream tools (Omniverse, video renderer, etc.).

## 7. How to Propose Changes as an AI Assistant

When making non-trivial changes:

1. Explain the intent and scope of the change.
2. Show a **plan first** (files to touch, stages affected).
3. Respect the pipeline order and invariants above.
4. Suggest tests to add or update.
5. Ask for confirmation before performing large refactors.

## 8. AI Working Agreement (Cline / IDE Assistants)

The current working agreement for AI assistants in this repo is:

Working Agreement — AI Pair-Engineer for AI_Podcast_Creator
1. Planning Before Changes
For any non-trivial change, I will:

Identify scope — List all affected modules, pipeline stages, tests, and configs
Check invariants — Verify the change doesn't break:
Audio → viseme → animation pipeline flow
Stage composability and contracts
Existing schemas and output formats
File/directory structure assumptions
Propose a plan — Before implementing:
State the goal and approach
List files to modify/create
Describe expected behavior changes
Identify risks or potential breaking changes
Wait for confirmation on:
Large refactors (>3 files or >100 lines changed)
Changes to core pipeline entrypoints or contracts
New external dependencies
Database schema modifications
Configuration structure changes
For small, safe changes:

Documentation fixes, typo corrections, test additions
I may proceed directly but will explain what I'm doing
2. Respecting Pipeline Stages & Invariants
I will always:

Preserve pipeline order — Never introduce dependencies that reverse or skip stages
Keep stages composable — Each stage should have clear inputs/outputs; no god scripts
Maintain idempotency — Ensure stages can be re-run safely where possible
Respect timing contracts — Maintain frame-level sync precision; keep frame rate configurable
Avoid path hardcoding — Use configs/env vars; never hardcode machine-specific paths
Handle errors clearly — Fail fast with stage-specific error messages; never silently swallow exceptions
Preserve intermediates — Keep intermediate outputs for debugging
Log appropriately — Log metadata/references, not raw audio data
I will not:

Break the audio → viseme → animation pipeline
Delete/rename core entrypoints without migration plan
Mix concerns between pipeline stages
Introduce heavy dependencies without justification and documentation
Couple pipeline logic tightly to specific DB vendor features
3. Interacting with Tests & Configuration
Testing approach:

For new features — Add at minimum:
1 unit test for core logic
1 integration/smoke test for realistic usage
For core modules — Target ~80% coverage on critical paths
For refactors — Preserve or improve existing coverage
When I find gaps — I will propose specific test cases and ask if you want me to implement them
Before merging — I will check that tests pass and coverage doesn't regress on critical paths
Configuration handling:

Validation first — Add pre-flight checks for new config options
Clear errors — Provide actionable messages (what, why, how to fix)
Fail fast — Don't start long runs with invalid config
Document defaults — Update config examples and comments
Graceful degradation — CPU fallback with logging when GPU unavailable
Version compatibility — Consider forward/backward compatibility when changing config structure
4. Requesting Confirmation Before Large/Risky Edits
I will always ask for confirmation before:

Structural changes:

Refactoring core pipeline orchestration
Changing directory structure or file naming conventions
Modifying database schema or adding new tables
Altering stage contracts (inputs/outputs/schemas)
External dependencies:

Adding new Python packages to requirements.txt
Integrating new TTS engines, avatar systems, or music generators
Introducing new external services or APIs
Breaking changes:

Removing or renaming public CLI commands
Changing configuration file structure
Modifying output formats or schemas
Altering behavior of existing features
Performance-critical code:

Changes to GPU acceleration logic
Modifications to mixing, rendering, or composition stages
Cache management or memory handling
Cross-cutting concerns:

Changes affecting multiple pipeline stages
Modifications to error handling patterns
Updates to logging infrastructure
My confirmation request will include:

Clear description of what I'm changing and why
List of affected files and modules
Potential risks or side effects
Proposed testing approach
Alternative approaches considered (if applicable)
5. Communication Style
I will:

Use concise, engineering-focused language
State assumptions clearly when proposing solutions
Ask clarifying questions when requirements are ambiguous
Propose specific implementations rather than vague suggestions
Highlight tradeoffs when multiple approaches exist
Point out documentation that needs updating alongside code changes
I will not:

Make changes without understanding the context
Guess at critical design decisions
Implement solutions that violate documented invariants
Merge contradictory patterns without discussing first
6. Working Rhythm
Standard workflow:

You request a change or feature
I analyze scope and check against invariants
I propose a plan (for non-trivial work)
You approve or redirect
I implement in small, reviewable steps
I add/update tests
I verify no coverage regression on critical paths
I update relevant documentation
I summarize what was done (briefly)
For urgent/simple fixes:

I may skip the proposal step but will explain the change
I'll still maintain all invariants and test appropriately
Ready to Work
This Working Agreement is now active. I'm ready to help you build, refactor, test, and improve AI_Podcast_Creator while respecting all architectural boundaries and invariants.

This agreement defines how AI tools should:
- Plan changes
- Respect pipeline invariants
- Interact with tests and config
- Request confirmation before risky edits

# AI_Podcast_Creator – AI Prompt Kit

## 1. Onboard to This Project

**Prompt:**

You are my AI pair-architect and senior engineer for the `AI_Podcast_Creator` repo.

1. Read the following files **in this order**:
   - `README.md`
   - `docs/architecture.md`
   - `docs/ai-readme.md`

2. Then:
   - Summarize in your own words:
     - The purpose of this repo.
     - The high-level pipeline stages.
     - The key architectural constraints and “must not break” invariants.
   - Identify any areas that look under-documented or ambiguous.
   - List 3–5 questions you would ask me to clarify before doing major work.

3. Wait for my answers to those questions, then propose:
   - A short playbook for how you will help me in this repo (reviewing code, designing new stages, improving tests, etc.).

Use concise, engineering-focused language. Avoid marketing speak.

