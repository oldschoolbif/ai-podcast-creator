# Decision 2: Backward Compatibility with Old Script Format

**Date:** 2025-11-03  
**Status:** Decided  
**Decider:** Development Team  
**Decision Date:** 2025-11-03

---

## Context

We're implementing a new advanced script format (Audacity/Descript style) with:
- Stage directions
- Pacing markers (`[pause Xs]`, `(beat)`)
- Complex sound cues with timing/volume
- Voice direction markers (`DEAN (tone):`)
- Production notes section

**Current system supports:**
- Simple `[MUSIC: description]` format
- Basic script parsing
- Simple music cue placement

**Question:** Should we maintain backward compatibility with the old `[MUSIC: ...]` format, or require all scripts to use the new format?

---

## Requirements

1. **User Experience**: Existing scripts should continue to work
2. **Migration Path**: Users should be able to adopt new format gradually
3. **Maintainability**: Code should not become overly complex
4. **Documentation**: Clear guidance on format differences
5. **Error Handling**: Clear messages if format is incompatible

---

## Options Considered

### Option A: Full Backward Compatibility (Auto-detect Format)

**Description:**
- Automatically detect which format a script uses
- Support both old `[MUSIC: ...]` and new advanced format
- Convert old format to new format internally if needed
- Provide warnings/suggestions to migrate

**Implementation:**
```python
class ScriptParserAdvanced:
    def parse(self, script_text: str):
        # Detect format
        if self._is_old_format(script_text):
            return self._parse_old_format(script_text)
        else:
            return self._parse_new_format(script_text)
    
    def _is_old_format(self, script_text: str) -> bool:
        # Simple heuristic: old format has [MUSIC:] but no [pause] or (beat)
        has_music_cue = "[MUSIC:" in script_text
        has_new_markers = "[pause" in script_text or "(beat)" in script_text
        return has_music_cue and not has_new_markers
```

**Pros:**
- ✅ **Zero breaking changes**: All existing scripts work immediately
- ✅ **Gradual migration**: Users can upgrade at their own pace
- ✅ **Lower risk**: No disruption to current workflows
- ✅ **Better UX**: Seamless transition for users
- ✅ **Documentation value**: Old format can serve as "simple mode"

**Cons:**
- ❌ **Code complexity**: Two parsing paths to maintain
- ❌ **Testing burden**: Need to test both formats
- ❌ **Potential confusion**: Users might mix formats
- ❌ **Maintenance cost**: Two codebases for parsing logic

**Implementation Complexity:** Medium  
**Time Estimate:** +1-2 days (for dual parser + detection logic)

---

### Option B: New Format Only (Breaking Change)

**Description:**
- Only support the new advanced format
- Old scripts will fail with clear error message
- Provide migration tool or documentation to convert old scripts
- Require users to update scripts before use

**Implementation:**
```python
class ScriptParserAdvanced:
    def parse(self, script_text: str):
        # Only parse new format
        # If old format detected, raise helpful error
        if self._detects_old_format(script_text):
            raise ScriptFormatError(
                "Old [MUSIC:] format no longer supported. "
                "Please use the new format or run: podcast-creator migrate script.txt"
            )
        return self._parse_new_format(script_text)
```

**Pros:**
- ✅ **Simpler codebase**: Single parsing path
- ✅ **Less maintenance**: One format to support
- ✅ **Forces modernization**: Users get new features
- ✅ **Cleaner architecture**: No legacy code

**Cons:**
- ❌ **Breaking change**: Existing scripts stop working
- ❌ **User friction**: Requires immediate migration
- ❌ **Support burden**: Users need help migrating
- ❌ **Risk**: May lose users who don't want to migrate

**Implementation Complexity:** Low  
**Time Estimate:** No additional time (single parser)

---

### Option C: Hybrid with Migration Tool

**Description:**
- Support both formats initially (auto-detect)
- Provide migration tool: `podcast-creator migrate script.txt`
- Show deprecation warnings for old format
- Set timeline to remove old format support (e.g., 6 months)
- Convert old format to new format on-the-fly

**Implementation:**
```python
class ScriptParserAdvanced:
    def parse(self, script_text: str):
        if self._is_old_format(script_text):
            print("⚠️ Warning: Using deprecated [MUSIC:] format. "
                  "Run 'podcast-creator migrate script.txt' to convert.")
            # Auto-convert old format to new format
            converted = self._convert_old_to_new(script_text)
            return self._parse_new_format(converted)
        return self._parse_new_format(script_text)
    
    def _convert_old_to_new(self, script_text: str) -> str:
        # Convert [MUSIC: description] to new format
        # [Intro music: description, -12dB, fade in 2s]
        ...
```

**Pros:**
- ✅ **Best of both**: Compatibility + migration path
- ✅ **User guidance**: Clear path forward
- ✅ **Flexible timeline**: Remove old format when ready
- ✅ **Lower friction**: Works immediately, migrates later
- ✅ **Documentation**: Migration tool teaches new format

**Cons:**
- ❌ **Initial complexity**: Need both parsers + converter
- ❌ **Long-term maintenance**: Keep old format code for deprecation period
- ❌ **Technical debt**: Eventually need to remove old code

**Implementation Complexity:** Medium-High  
**Time Estimate:** +2-3 days (parser + converter + migration tool)

---

### Option D: Feature Flag / Config Option

**Description:**
- Support both formats with a config flag
- Default: new format (with auto-detection fallback)
- Config option: `script_format: legacy | auto | modern`
- Users can opt-in to old format support
- New installations default to modern format

**Implementation:**
```python
# config.yaml
script:
  format: "auto"  # auto, legacy, modern
  legacy_warning: true

class ScriptParserAdvanced:
    def parse(self, script_text: str):
        format_mode = self.config.get("script", {}).get("format", "auto")
        
        if format_mode == "legacy":
            return self._parse_old_format(script_text)
        elif format_mode == "modern":
            return self._parse_new_format(script_text)
        else:  # auto
            # Auto-detect and warn
            ...
```

**Pros:**
- ✅ **User control**: Let users choose format
- ✅ **Flexible**: Can change behavior via config
- ✅ **Backward compatible**: Can enable old format
- ✅ **Clear separation**: Explicit format choice

**Cons:**
- ❌ **Configuration complexity**: More options to understand
- ❌ **Potential confusion**: Which format should I use?
- ❌ **Maintenance**: Still need both parsers

**Implementation Complexity:** Medium  
**Time Estimate:** +1-2 days (config + dual parser)

---

## Decision Criteria

Rate each option (1-5 scale) on:

### 1. User Experience
- **Option A (Full Compatibility)**: ⭐⭐⭐⭐⭐ (Seamless, no changes needed)
- **Option B (New Only)**: ⭐⭐ (Breaking, requires migration)
- **Option C (Hybrid + Migration)**: ⭐⭐⭐⭐ (Works + guided upgrade)
- **Option D (Feature Flag)**: ⭐⭐⭐⭐ (Flexible but requires config)

### 2. Code Maintainability
- **Option A**: ⭐⭐⭐ (Two parsers to maintain)
- **Option B**: ⭐⭐⭐⭐⭐ (Single parser, clean)
- **Option C**: ⭐⭐⭐ (Two parsers + converter)
- **Option D**: ⭐⭐⭐ (Two parsers + config)

### 3. Development Speed
- **Option A**: ⭐⭐⭐ (Need dual parser)
- **Option B**: ⭐⭐⭐⭐⭐ (Fastest, single parser)
- **Option C**: ⭐⭐⭐ (Parser + converter + tool)
- **Option D**: ⭐⭐⭐⭐ (Parser + config logic)

### 4. Risk Assessment
- **Option A**: ⭐⭐⭐⭐⭐ (Lowest risk, no breakage)
- **Option B**: ⭐⭐ (High risk of user disruption)
- **Option C**: ⭐⭐⭐⭐ (Low risk, migration path)
- **Option D**: ⭐⭐⭐⭐ (Low risk, configurable)

### 5. Long-term Sustainability
- **Option A**: ⭐⭐⭐ (Tech debt of maintaining two parsers)
- **Option B**: ⭐⭐⭐⭐⭐ (Clean, single direction)
- **Option C**: ⭐⭐⭐⭐ (Migration path, eventual cleanup)
- **Option D**: ⭐⭐⭐ (Permanent dual support)

### 6. User Adoption of New Features
- **Option A**: ⭐⭐⭐ (Users may stick to old format)
- **Option B**: ⭐⭐⭐⭐⭐ (Forces adoption)
- **Option C**: ⭐⭐⭐⭐ (Encourages migration)
- **Option D**: ⭐⭐⭐ (Users may prefer old format)

---

## Scoring Matrix

| Criterion | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| User Experience | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Maintainability | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Development Speed | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Risk | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Sustainability | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Feature Adoption | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Total** | **20/30** | **22/30** | **23/30** | **21/30** |

---

## Questions to Consider

### 1. User Base Impact
**Q:** How many existing scripts/users will be affected?
- **Many existing scripts**: → Option A or C
- **Few/new project**: → Option B (clean slate)
- **Unknown**: → Option C (safe default)

### 2. Migration Timeline
**Q:** Can users migrate immediately, or need time?
- **Immediate migration OK**: → Option B
- **Need gradual migration**: → Option A or C
- **Want user control**: → Option D

### 3. Support Resources
**Q:** Can you provide migration support/tools?
- **Yes, can provide tools**: → Option C (best path)
- **Limited support**: → Option A (easiest for users)
- **No support available**: → Option B (force migration)

### 4. Technical Debt Tolerance
**Q:** Are you OK maintaining two parsers temporarily?
- **Yes, for migration period**: → Option C
- **Prefer clean codebase**: → Option B
- **Want flexibility**: → Option D

### 5. Documentation & Onboarding
**Q:** Can you provide clear migration docs?
- **Yes, comprehensive docs**: → Option C (best with docs)
- **Minimal docs**: → Option A (works without docs)
- **User self-service**: → Option D (config-based)

---

## Real-World Examples

### Similar Decisions:

**Python 2 → 3 Migration:**
- Initially: Both versions supported
- Eventually: Python 2 deprecated
- **Lesson**: Gradual migration with deprecation works

**Django LTS Versions:**
- Support old versions with deprecation warnings
- Provide migration guides
- **Lesson**: Clear migration path is key

**React Hooks:**
- Class components still work (backward compatible)
- New hooks encouraged but not required
- **Lesson**: Optional adoption works well

---

## My Recommendation

**Option C: Hybrid with Migration Tool**

**Rationale:**
1. ✅ **Safest for users**: Zero breaking changes immediately
2. ✅ **Clear path forward**: Migration tool guides users
3. ✅ **Best adoption**: Encourages new format without forcing
4. ✅ **Manageable tech debt**: Can remove old format after migration period
5. ✅ **Professional approach**: Deprecation warnings show maturity

**Implementation Strategy:**
1. **Phase 1 (Now)**: Implement both parsers + auto-detection
2. **Phase 2 (Next release)**: Add migration tool + deprecation warnings
3. **Phase 3 (6 months)**: Remove old format support

**Accepted Trade-offs:**
- Maintain two parsers for ~6 months
- Additional 2-3 days development time
- Need to write migration tool

**Rejected Options:**
- **Option B**: Too risky - may lose users
- **Option A**: No migration path - tech debt forever
- **Option D**: Too complex - users confused by config

---

## Implementation Notes

If choosing Option C:

### 1. Detection Logic
```python
def _is_old_format(self, script_text: str) -> bool:
    """Detect if script uses old [MUSIC:] format"""
    # Old format indicators:
    # - Has [MUSIC: ...] markers
    # - No [pause ...] markers
    # - No (beat) markers
    # - No voice direction markers like "DEAN (tone):"
    # - No production notes section
    
    has_old_music = bool(re.search(r'\[MUSIC:\s*[^\]]+\]', script_text))
    has_new_markers = (
        '[pause' in script_text or
        '(beat)' in script_text or
        re.search(r'^[A-Z]+\s*\([^)]+\):', script_text, re.MULTILINE) or
        'Production Notes:' in script_text
    )
    
    return has_old_music and not has_new_markers
```

### 2. Migration Tool Structure
```python
@app.command()
def migrate(
    script_path: Path = typer.Argument(..., help="Script file to migrate"),
    output_path: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file (default: overwrite original)"),
):
    """Migrate old script format to new format."""
    # Read old format
    # Convert [MUSIC: ...] to new sound cue format
    # Add production notes template
    # Save new format
```

### 3. Converter Logic
```python
def _convert_old_to_new(self, script_text: str) -> str:
    """Convert old [MUSIC: description] to new format"""
    # Pattern: [MUSIC: calm ambient]
    # Convert to: [Intro music: calm ambient, -12dB, fade in 2s → underlay]
    
    def replace_music(match):
        desc = match.group(1).strip()
        return f"[Intro music: {desc}, -12dB, fade in 2s → underlay for duration]"
    
    converted = re.sub(r'\[MUSIC:\s*([^\]]+)\]', replace_music, script_text)
    return converted
```

---

## Consequences

**Positive:**
- ✅ All existing scripts continue to work
- ✅ Users can adopt new format at their pace
- ✅ Clear migration path provided
- ✅ Professional deprecation handling

**Negative:**
- ❌ Need to maintain two parsers temporarily
- ❌ Additional code complexity
- ❌ Migration tool development effort

**Mitigation:**
- Set clear timeline (6 months) for removing old format
- Write comprehensive migration guide
- Provide migration tool with preview/dry-run
- Add deprecation warnings to encourage migration

---

## Follow-up Decisions

Decisions that depend on this:
- [ ] Decision 3: Timing Precision (affects timeline builder)
- [ ] Decision 4: Pause Implementation (TTS-integrated vs post-process)
- [ ] Script format documentation structure

---

## Review Date

**Next Review:** 2025-05-03 (6 months, to assess migration progress)

---

## Decision

**Selected Option:** Option B - New Format Only (Breaking Change)

**Rationale:**
- ✅ **Private alpha phase**: No existing production users to break
- ✅ **Cleanest architecture**: Single parser path, no legacy code
- ✅ **Best value**: Focus on new format features, not maintaining old code
- ✅ **Faster implementation**: No dual parser complexity
- ✅ **Future-proof**: Start with best format from day one

**Accepted Trade-offs:**
- No backward compatibility needed (alpha phase advantage)
- Old `[MUSIC:]` format will not be supported
- Users must use new advanced format

**Implementation:**
- Implement only new format parser
- Clear error message if old format detected
- Focus development time on new features

---

## Consequences

**Positive:**
- ✅ Single, clean codebase
- ✅ Faster development (no dual parser)
- ✅ Best-in-class features from start
- ✅ No technical debt from legacy code

**Negative:**
- ❌ Old format scripts won't work (acceptable in alpha)

**Mitigation:**
- Clear error message pointing to new format
- Good documentation of new format
- Example scripts in new format

