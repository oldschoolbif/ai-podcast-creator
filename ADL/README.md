# Architecture Decision Logs (ADL)

This directory contains architecture decision records (ADRs) for the AI Podcast Creator project. Each decision document follows a structured format to capture the context, options, and rationale for important technical choices.

## Structure

- `00_HISTORICAL_DECISIONS.md` - **COMPLETE historical log of ALL decisions (65 decisions documented)**
- `00_DECISION_TEMPLATE.md` - Template for creating new decision documents
- `00_NEXT_ITERATION_PLAN.md` - Overall plan for next iteration features
- `01_DECISION_AUDIO_EFFECTS.md` - Decision on audio effects library (pedalboard vs. build from scratch)
- `02_DECISION_BACKWARD_COMPATIBILITY.md` - Decision on backward compatibility with old script format
- `03_DECISION_TIMING_PRECISION.md` - Decision on timing precision for audio timeline
- `04_DECISION_PAUSE_IMPLEMENTATION.md` - Decision on pause insertion strategy
- `IMPLEMENTATION_SUMMARY.md` - Summary of implementation plan based on all decisions

## Purpose

These documents serve to:
- 📝 **Document decisions**: Capture why choices were made, not just what was chosen
- 🔍 **Enable review**: Allow future review and reconsideration of decisions
- 🧠 **Share context**: Help new team members understand past decisions
- 🔄 **Track evolution**: Show how architecture evolves over time

## Creating New Decisions

1. Copy `00_DECISION_TEMPLATE.md`
2. Name it `XX_DECISION_[TOPIC].md` (where XX is the next number)
3. Fill in all sections thoughtfully
4. Update this README with the new decision

## Decision Status

- **Pending**: Decision not yet made, awaiting input
- **Decided**: Decision made, documented
- **Implemented**: Decision implemented in code
- **Superseded**: Decision replaced by newer decision

## Review Process

Each decision should be reviewed periodically (typically every 6-12 months) to ensure it still makes sense given:
- Changes in requirements
- New technologies available
- Lessons learned from implementation
- User feedback

---

## Active Decisions

| # | Topic | Status | Decision | Date |
|---|-------|--------|----------|------|
| 1 | Audio Effects Library | Decided | Option C (pedalboard + pydub hybrid) | 2025-11-03 |
| 2 | Backward Compatibility | Decided | Option B (new format only, no backward compatibility) | 2025-11-03 |
| 3 | Timing Precision | Decided | Option C+D Hybrid (configurable, frame-based for video, time-based for audio) | 2025-11-03 |
| 4 | Pause Implementation | Decided | Option C Hybrid (SSML for Coqui, post-process for gTTS, quality-focused) | 2025-11-03 |

---

## Decision History

*Decisions will be archived here once superseded or finalized*

