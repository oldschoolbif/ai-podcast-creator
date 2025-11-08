# Implementation Plan - AI Podcast Creator

**Created:** 2025-11-03  
**Last Updated:** 2025-11-03  
**Status:** Ready for Execution  
**Principle:** QA-first development embedded in every phase

---

## Overview

This document outlines the phased implementation plan aligned with the [Roadmap](ROADMAP.md). Tasks are ordered by priority within each phase and organized to show dependencies and parallel work opportunities.

**Key Principles:**
- QA embedded in every task
- Build incrementally with working increments
- Test continuously
- Document as we go

---

## Phase 1: Building the Foundation (Current Phase)

**Focus:** Complete core functionality, hardware optimization, universal compatibility  
**Status:** In Progress

### Sprint 1.1: Complete Background Image Selection

**Priority:** High  
**Goal:** Enable custom background image selection via CLI and UI

**Tasks:**
1. **CLI Enhancement** (`src/cli/main.py`)
   - [ ] Add `--background-image <path>` option
   - [ ] Validate image file exists and is valid format
   - [ ] Pass custom path to `VideoComposer`
   - [ ] Update help text and documentation

2. **Desktop GUI Enhancement** (`src/gui/desktop_gui.py`)
   - [ ] Add file browser button for background selection
   - [ ] Display selected image path
   - [ ] Validate image format (JPG, PNG, etc.)
   - [ ] Preview image before selection (optional)

3. **Web GUI Enhancement** (`src/gui/web_interface.py`)
   - [ ] Add file upload component for background
   - [ ] Handle image upload and temporary storage
   - [ ] Display upload status
   - [ ] Pass file path to backend

4. **Video Composer Update** (`src/core/video_composer.py`)
   - [ ] Accept optional `background_image_path` parameter
   - [ ] Use custom path if provided, fallback to default
   - [ ] Maintain existing scaling and padding logic

5. **QA Requirements:**
   - [ ] Unit tests for image validation
   - [ ] Integration test for CLI custom background
   - [ ] Integration test for GUI file selection
   - [ ] Test with various image formats (JPG, PNG, WebP)
   - [ ] Test with different aspect ratios

**Dependencies:** None  
**Estimated Effort:** 2-3 days

---

### Sprint 1.2: Advanced Script Format Support

**Priority:** High  
**Goal:** Parse and process new script format with stage directions, pacing, sound cues

**Tasks:**
1. **Enhanced Script Parser** (`src/core/script_parser_advanced.py` - NEW)
   - [ ] Parse stage directions (`[Intro music: ...]`)
   - [ ] Parse pacing markers (`[pause Xs]`, `(beat)`)
   - [ ] Parse sound cues with parameters (`[MUSIC: description, -12dB, fade in 2s]`)
   - [ ] Parse voice direction markers (`DEAN (tone):`)
   - [ ] Parse production notes section
   - [ ] Extract metadata (WPM target, tone, processing settings)

2. **Timeline Composer** (`src/core/timeline_composer.py` - NEW)
   - [ ] Implement configurable precision (per Decision 3)
   - [ ] Auto-select precision based on media type (video = frame-based, audio = time-based)
   - [ ] Build timeline structure with TTS segments, pauses, sound cues
   - [ ] Map script character positions to audio timestamps
   - [ ] Support future precision upgrades

3. **Pause Processor** (`src/core/pause_processor.py` - NEW)
   - [ ] Implement post-processing pauses for gTTS (high-quality)
   - [ ] Character-to-audio timestamp mapping
   - [ ] Short crossfades (5-10ms) to prevent clicks
   - [ ] Beat pause handling (default 0.5s)
   - [ ] SSML support for Coqui (Phase 2)
   - [ ] Engine detection and routing logic

4. **Configuration Updates** (`config.yaml`)
   - [ ] Add timeline precision settings
   - [ ] Add pause processing configuration
   - [ ] Add default beat duration

5. **Integration** (`src/cli/main.py`, `src/core/tts_engine.py`)
   - [ ] Replace `ScriptParser` with `ScriptParserAdvanced`
   - [ ] Integrate `TimelineComposer` into TTS workflow
   - [ ] Integrate `PauseProcessor` into audio generation

6. **QA Requirements:**
   - [ ] Unit tests for each parser component
   - [ ] Integration test with test script (`FRB fully featured test.txt`)
   - [ ] Timing accuracy validation (±100ms for audio, ±33ms for video)
   - [ ] Pause quality tests (natural-sounding)
   - [ ] Edge case tests (empty pauses, overlapping cues)

**Dependencies:** Architecture Decisions 2-4  
**Estimated Effort:** 5-7 days

---

### Sprint 1.3: Sound Cue Processing & Enhanced Audio Mixing

**Priority:** High  
**Goal:** Handle complex sound cues and multi-stream audio mixing

**Tasks:**
1. **Sound Cue Processor** (`src/core/sound_cue_processor.py` - NEW)
   - [ ] Parse sound cue parameters (volume, fade, duration)
   - [ ] Generate fade in/out curves
   - [ ] Volume automation (+/-XdB adjustments)
   - [ ] Support layered sounds (multiple cues simultaneously)
   - [ ] Timing synchronization with timeline

2. **Enhanced Audio Mixer** (`src/core/enhanced_audio_mixer.py` - NEW)
   - [ ] Support multiple music segments (intro, underscore, emotional lift, outro)
   - [ ] Precise timing control (when each stream starts/stops)
   - [ ] Volume automation per stream
   - [ ] Fade curves per stream
   - [ ] Dynamic ducking (voice activity detection - optional)
   - [ ] Support for sound effects layer
   - [ ] Support for custom recording integration

3. **Timeline Integration** (`src/core/timeline_composer.py`)
   - [ ] Integrate sound cue processing
   - [ ] Synchronize sound cues with TTS timeline
   - [ ] Handle multiple overlapping cues
   - [ ] Generate final mixed audio output

4. **CLI/UI Updates**
   - [ ] Support for sound effect files
   - [ ] Support for custom recording files
   - [ ] Multi-track preview (future)

5. **QA Requirements:**
   - [ ] Multi-stream mixing tests (4+ streams)
   - [ ] Timing accuracy validation (±100ms target)
   - [ ] Audio quality tests (no clipping, distortion)
   - [ ] Fade curve validation
   - [ ] Performance tests with many streams

**Dependencies:** Sprint 1.2 (Timeline Composer)  
**Estimated Effort:** 4-6 days

---

### Sprint 1.4: Professional Audio Processing

**Priority:** Medium  
**Goal:** Implement professional audio effects (EQ, compression, reverb, de-esser)

**Tasks:**
1. **Install Dependencies**
   - [ ] Add `pedalboard>=0.7.0` to `requirements.txt`
   - [ ] Test installation and compatibility

2. **Audio Processor** (`src/core/audio_processor.py` - NEW)
   - [ ] EQ implementation (low-cut at 90Hz, presence boost at 4kHz)
   - [ ] Compression (-3dB threshold, 3:1 ratio)
   - [ ] Reverb (small space, subtle)
   - [ ] De-esser (light on s/ch sounds)
   - [ ] Audio normalization
   - [ ] Chain effects in correct order

3. **Production Notes Integration** (`src/core/script_parser_advanced.py`)
   - [ ] Parse audio processing settings from script
   - [ ] Extract EQ, compression, reverb parameters
   - [ ] Generate configuration from production notes

4. **Configuration** (`config.yaml`)
   - [ ] Add audio processing settings
   - [ ] Allow override from production notes
   - [ ] Default processing chain

5. **Integration** (`src/cli/main.py`)
   - [ ] Apply audio processing after mixing
   - [ ] Optional: preview before/after processing

6. **QA Requirements:**
   - [ ] Audio quality validation (no artifacts)
   - [ ] Processing chain tests
   - [ ] Configuration parsing tests
   - [ ] Performance tests (processing speed)

**Dependencies:** Architecture Decision 1 (pedalboard selection)  
**Estimated Effort:** 3-4 days

---

### Sprint 1.5: TTS GPU Optimization

**Priority:** Medium  
**Goal:** Maximize TTS performance using all available hardware

**Tasks:**
1. **Model Optimization** (`src/core/tts_engine.py`)
   - [ ] Implement model quantization (INT8/FP16)
   - [ ] ONNX conversion for faster inference (optional)
   - [ ] torch.compile integration (PyTorch 2.0+)
   - [ ] Memory-efficient batching

2. **Pipeline Parallelization**
   - [ ] Parallel preprocessing and inference
   - [ ] Multi-threading where applicable
   - [ ] GPU memory pooling

3. **Performance Monitoring**
   - [ ] GPU utilization tracking
   - [ ] Speed benchmarks
   - [ ] Performance regression detection

4. **Batch Processing**
   - [ ] Support for multiple scripts
   - [ ] Cache optimization for repeated segments
   - [ ] Parallel script processing

5. **Configuration** (`config.yaml`)
   - [ ] Enable/disable optimizations
   - [ ] Batch size configuration
   - [ ] Performance logging

6. **QA Requirements:**
   - [ ] Performance regression tests
   - [ ] Speed benchmarks (< 5s for 1-min speech target)
   - [ ] GPU utilization monitoring (> 80% target)
   - [ ] Output quality validation (no degradation)

**Dependencies:** None (can be parallel with other sprints)  
**Estimated Effort:** 4-5 days

---

### Sprint 1.6: Enhanced Visualization Styles

**Priority:** Low (Future Enhancement)  
**Goal:** Expand visualization beyond basic waveform

**Tasks:**
1. **Enhanced Waveform Styles** (`src/core/audio_visualizer.py`)
   - [ ] Bar visualization style
   - [ ] Circular visualization style
   - [ ] Spectrum analyzer style
   - [ ] Style selection via config/CLI

2. **Text Overlays** (`src/core/video_composer.py`)
   - [ ] Subtitles generation
   - [ ] Title overlays
   - [ ] Caption support

3. **Graphics Overlays**
   - [ ] Logo overlay support
   - [ ] Icon overlays
   - [ ] Custom graphics integration

4. **UI/CLI Updates**
   - [ ] Visualization style selector
   - [ ] Text overlay configuration
   - [ ] Graphics upload/preview

5. **QA Requirements:**
   - [ ] Visual regression tests
   - [ ] Performance tests (FPS during visualization)
   - [ ] Style switching tests

**Dependencies:** Sprint 1.1 (Background selection)  
**Estimated Effort:** 5-7 days

---

### Sprint 1.7: QA Infrastructure Enhancement

**Priority:** Continuous (Parallel with all sprints)  
**Goal:** Improve QA processes and tooling

**Tasks:**
1. **Automated QA Reports**
   - [ ] Generate coverage reports
   - [ ] Track coverage trends
   - [ ] Performance regression tracking
   - [ ] Quality metrics dashboard

2. **Intelligent Tooling**
   - [ ] Mutation testing automation (mutmut)
   - [ ] Property-based test generation (hypothesis)
   - [ ] Fuzz testing for edge cases
   - [ ] Automated test case generation from bugs

3. **Playback Validation Suite**
   - [ ] Automated playback tests (multiple players)
   - [ ] Variable speed playback tests
   - [ ] Cross-platform validation
   - [ ] Streaming platform compatibility tests

4. **Documentation**
   - [ ] Test coverage targets documented
   - [ ] QA process documentation
   - [ ] Tooling setup guides

**Dependencies:** None (continuous improvement)  
**Estimated Effort:** Ongoing

---

## Phase 2: Enhanced Audio & Visuals (Next Phase)

**Focus:** Advanced graphics, professional audio processing, visualization expansion

### Sprint 2.1: Advanced Visualization Options

**Tasks:**
1. **Particle Systems** (`src/core/audio_visualizer.py`)
   - [ ] Particle system implementation
   - [ ] Audio-reactive particles
   - [ ] GPU-accelerated rendering

2. **Data Visualization**
   - [ ] Data-driven graphics
   - [ ] Animated backgrounds
   - [ ] Dynamic text effects

3. **Multi-Layer Compositing**
   - [ ] Support multiple visualization layers
   - [ ] Layer blending modes
   - [ ] Layer opacity control

**Dependencies:** Phase 1 Sprint 1.6  
**Estimated Effort:** 7-10 days

---

### Sprint 2.2: Advanced Script Format Completion

**Tasks:**
1. **Full Production Notes Processing**
   - [ ] Complete metadata extraction
   - [ ] WPM targeting implementation
   - [ ] Tone variation support

2. **Voice Direction Implementation**
   - [ ] Tone parameter extraction
   - [ ] Speed variation
   - [ ] Apply to TTS engine parameters

**Dependencies:** Phase 1 Sprint 1.2  
**Estimated Effort:** 3-4 days

---

### Sprint 2.3: SSML Pause Support (Quality Enhancement)

**Tasks:**
1. **SSML Integration for Coqui** (`src/core/pause_processor.py`)
   - [ ] SSML conversion for Coqui TTS
   - [ ] Break timing accuracy
   - [ ] Voice-appropriate pause durations

2. **Engine Detection & Routing**
   - [ ] Automatic SSML for SSML-capable engines
   - [ ] Fallback to post-processing
   - [ ] Quality validation

**Dependencies:** Phase 1 Sprint 1.2  
**Estimated Effort:** 2-3 days

---

## Phase 3: AI Avatar Evolution (Future)

**Focus:** Replace static image with quality AI avatar, lip-sync

### Sprint 3.1: High-Quality AI Avatar

**Tasks:**
1. **Avatar Generation Pipeline Improvement**
   - [ ] Optimize Wav2Lip integration
   - [ ] Enhance SadTalker support
   - [ ] Improve lip-sync accuracy (> 95% target)

2. **Natural Animation**
   - [ ] Head movement implementation
   - [ ] Eye contact and blinking
   - [ ] Expressive animations

3. **High-Resolution Output**
   - [ ] 1080p+ avatar rendering
   - [ ] Quality vs. speed configuration

**Dependencies:** Phase 1 foundation  
**Estimated Effort:** 10-15 days

---

### Sprint 3.2: Avatar Customization

**Tasks:**
1. **Custom Avatar Upload**
   - [ ] Avatar image upload (CLI/UI)
   - [ ] Avatar validation
   - [ ] Style presets

2. **Expression Control**
   - [ ] Expression intensity settings
   - [ ] Movement control
   - [ ] Positioning and scaling

**Dependencies:** Sprint 3.1  
**Estimated Effort:** 4-6 days

---

## Phase 4: Multi-Character System (Future)

**Focus:** Multiple actors, unique voices, character interactions

### Sprint 4.1: Multiple Actors Support

**Tasks:**
1. **Multi-Character Script Format**
   - [ ] Character assignment parsing
   - [ ] Scene layout management
   - [ ] Character switching logic

2. **Multi-Avatar Rendering**
   - [ ] Multiple avatar generation pipeline
   - [ ] Layout management (grid, splitscreen)
   - [ ] Character positioning

3. **Voice Per Character**
   - [ ] Character-to-voice mapping
   - [ ] Multiple TTS engine support
   - [ ] Voice consistency

**Dependencies:** Phase 3 foundation  
**Estimated Effort:** 15-20 days

---

## Phase 5: AI Round Table (Future)

**Focus:** Full multi-character dialogue with human expressions

### Sprint 5.1: Advanced Character Expressions

**Tasks:**
1. **Expression System**
   - [ ] Expression markers in script
   - [ ] Avatar expression implementation
   - [ ] Audio generation for expressions (sighing, laughing, coughing)

2. **Round Table Dynamics**
   - [ ] Multi-character dialogue system
   - [ ] Character interactions
   - [ ] Turn-taking and conversation flow

**Dependencies:** Phase 4 foundation  
**Estimated Effort:** 20-30 days

---

## Implementation Guidelines

### Task Organization

1. **Dependencies First:** Complete foundational tasks before dependent ones
2. **Parallel Work:** Identify tasks that can be done simultaneously
3. **Incremental Value:** Each sprint delivers working functionality
4. **QA Embedded:** Tests written alongside implementation

### Sprint Structure

Each sprint follows this pattern:

1. **Planning (Day 1)**
   - Review requirements
   - Identify dependencies
   - Break down tasks
   - Set success criteria

2. **Implementation (Days 2-N)**
   - Code implementation
   - Write tests alongside code
   - Continuous integration checks

3. **Testing & QA (Final Day)**
   - Integration testing
   - QA review
   - Performance validation
   - Documentation updates

### Quality Gates

Before a sprint is considered complete:

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Performance benchmarks met (if applicable)
- [ ] Code coverage maintained/improved
- [ ] Documentation updated
- [ ] Code reviewed (self-review minimum)

### Continuous Improvement

- End of each sprint: QA review
- Identify process improvements
- Update tooling if needed
- Document learnings

---

## Success Criteria Summary

### Phase 1: Building the Foundation
- ✅ Custom background selection (CLI + UI)
- ✅ Advanced script format fully parsed
- ✅ Timeline-based audio composition
- ✅ Professional audio processing
- ✅ Multi-stream audio mixing
- ✅ TTS optimized for speed
- ✅ Test coverage > 40%

### Phase 2: Enhanced Audio & Visuals
- ✅ Multiple visualization styles
- ✅ Full production notes support
- ✅ SSML pause support for Coqui

### Phase 3: AI Avatar Evolution
- ✅ Avatar lip-sync > 95% accuracy
- ✅ Natural animations
- ✅ Custom avatar support

### Phase 4: Multi-Character System
- ✅ 4 characters in one video
- ✅ Unique voices per character
- ✅ Flexible layouts

### Phase 5: AI Round Table
- ✅ Human-like expressions
- ✅ Natural conversation dynamics
- ✅ Multi-character interactions

---

## Notes

- **Flexibility:** Priorities can be reordered based on learnings
- **QA First:** Every feature ships with quality assurance
- **Time Tracking:** Actual completion times recorded in ROADMAP.md
- **Architecture Decisions:** All decisions documented in ADL/
- **Dependencies:** New libraries documented as they're added

---

**Last Updated:** 2025-11-03  
**Next Review:** End of current sprint

