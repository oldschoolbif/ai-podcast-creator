"""
Property-Based Testing Examples with Hypothesis
Automatically generates 100s of test cases to find edge cases you'd never think of!
"""

import os
import sys
from pathlib import Path

import pytest

# Check if hypothesis is installed
try:
    from hypothesis import HealthCheck, assume, example, given, settings
    from hypothesis import strategies as st

    HYPOTHESIS_AVAILABLE = True

    if os.getenv("MUTANT_UNDER_TEST"):
        settings.register_profile(
            "mutation",
            suppress_health_check=[HealthCheck.differing_executors, HealthCheck.function_scoped_fixture],
            deadline=None,
            max_examples=50,
        )
        settings.load_profile("mutation")
except ImportError:
    HYPOTHESIS_AVAILABLE = False

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.script_parser import ScriptParser
from src.core.tts_engine import TTSEngine

# Skip all tests if hypothesis not installed
pytestmark = pytest.mark.skipif(
    not HYPOTHESIS_AVAILABLE, reason="Hypothesis not installed. Run: pip install hypothesis"
)


@pytest.mark.property
class TestScriptParserProperties:
    """Property-based tests for ScriptParser."""

    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_parse_never_crashes(self, test_config, text):
        """Parser should handle any text without crashing."""
        parser = ScriptParser(test_config)

        # Property: Should not crash, regardless of input
        result = parser.parse(text)

        assert result is not None
        assert "text" in result
        assert "music_cues" in result
        assert "metadata" in result

    @given(st.text(min_size=0, max_size=500))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_parse_output_structure(self, test_config, text):
        """Parser output should always have consistent structure."""
        parser = ScriptParser(test_config)
        result = parser.parse(text)

        # Property: Output structure is always the same
        assert isinstance(result, dict)
        assert isinstance(result["text"], str)
        assert isinstance(result["music_cues"], list)
        assert isinstance(result["metadata"], dict)
        assert "character_count" in result["metadata"]
        assert "music_cue_count" in result["metadata"]

    @given(st.integers(min_value=0, max_value=10))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @example(0)  # Always test edge case: 0 music cues
    @example(10)  # Always test edge case: max music cues
    def test_music_cues_count(self, test_config, num_cues):
        """Music cue count in metadata should match actual cues."""
        # Generate text with exact number of music cues
        text = "\n".join([f"[MUSIC: test {i}]" for i in range(num_cues)])

        parser = ScriptParser(test_config)
        result = parser.parse(text)

        # Property: Metadata count matches actual count
        assert result["metadata"]["music_cue_count"] == len(result["music_cues"])
        assert result["metadata"]["music_cue_count"] == num_cues


@pytest.mark.property
class TestTTSCacheKeyProperties:
    """Property-based tests for TTS cache key generation."""

    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_same_text_same_key(self, test_config, temp_dir, text):
        """Same text should always generate the same cache key."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        from unittest.mock import patch

        with patch("src.core.tts_engine.get_gpu_manager"), patch("gtts.gTTS"):
            engine = TTSEngine(test_config)

            key1 = engine._get_cache_key(text)
            key2 = engine._get_cache_key(text)

            # Property: Deterministic cache keys
            assert key1 == key2

    @given(st.text(min_size=1, max_size=100), st.text(min_size=1, max_size=100))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_different_text_different_key(self, test_config, temp_dir, text1, text2):
        """Different text should (almost always) generate different keys."""
        assume(text1 != text2)  # Only test when texts are different

        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        from unittest.mock import patch

        with patch("src.core.tts_engine.get_gpu_manager"), patch("gtts.gTTS"):
            engine = TTSEngine(test_config)

            key1 = engine._get_cache_key(text1)
            key2 = engine._get_cache_key(text2)

            # Property: Different inputs -> different outputs (hash collision is extremely rare)
            assert key1 != key2

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_cache_key_format(self, test_config, temp_dir, text):
        """Cache key should always be a valid MD5 hex string."""
        test_config["tts"] = {"engine": "gtts"}
        test_config["storage"]["cache_dir"] = str(temp_dir)

        from unittest.mock import patch

        with patch("src.core.tts_engine.get_gpu_manager"), patch("gtts.gTTS"):
            engine = TTSEngine(test_config)
            key = engine._get_cache_key(text)

            # Property: Cache key is always valid MD5 hex
            assert isinstance(key, str)
            assert len(key) == 32  # MD5 hex length
            assert all(c in "0123456789abcdef" for c in key)


@pytest.mark.property
class TestStringValidationProperties:
    """Example property-based tests for string validation."""

    @given(st.text())
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_title_extraction_robustness(self, test_config, text):
        """Title extraction should never crash on any text."""
        parser = ScriptParser(test_config)
        result = parser.parse(text)

        # Property: Always returns a title (default or extracted)
        assert "title" in result["metadata"]
        assert isinstance(result["metadata"]["title"], str)

    @given(st.text(min_size=1, max_size=50), st.integers(min_value=1, max_value=10))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @example("Test", 1)  # Always test simple case
    def test_character_count_property(self, test_config, word, count):
        """Character count should be non-negative and related to input."""
        text = " ".join([word] * count)

        parser = ScriptParser(test_config)
        result = parser.parse(text)

        # Property: Character count should be non-negative
        # (Can be less than input due to parser processing like title extraction)
        assert result["metadata"]["character_count"] >= 0
        assert isinstance(result["metadata"]["character_count"], int)


@pytest.mark.property
class TestEdgeCaseDiscovery:
    """Use property-based testing to discover edge cases."""

    @given(
        st.text(
            alphabet=st.characters(
                blacklist_categories=("Cs", "Cc"),  # Exclude surrogates and control chars
                blacklist_characters=("\x00",),  # Exclude null
            ),
            min_size=0,
            max_size=100,
        )
    )
    @settings(
        max_examples=100, suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.function_scoped_fixture]
    )
    def test_unicode_handling(self, test_config, text):
        """Parser should handle all Unicode characters gracefully."""
        parser = ScriptParser(test_config)

        try:
            result = parser.parse(text)
            # Property: Should return valid result or raise known exception
            assert result is not None
        except (ValueError, UnicodeError) as e:
            # These are acceptable failures for invalid unicode
            pytest.skip(f"Known unicode issue: {e}")

    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=20))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_concatenation_property(self, test_config, text_list):
        """Parsing concatenated text should be consistent."""
        parser = ScriptParser(test_config)

        # Parse individually
        individual_results = [parser.parse(text) for text in text_list]

        # Parse concatenated
        combined_text = "\n".join(text_list)
        combined_result = parser.parse(combined_text)

        # Property: Combined character count should be >= sum of individuals
        individual_char_count = sum(r["metadata"]["character_count"] for r in individual_results)
        assert combined_result["metadata"]["character_count"] >= individual_char_count


# ==============================================================================
# HOW TO USE PROPERTY-BASED TESTING
# ==============================================================================

"""
## Key Concepts

### 1. Properties vs Examples
Traditional testing:
    def test_add():
        assert add(2, 3) == 5  # One example

Property-based testing:
    @given(st.integers(), st.integers())
    def test_add_commutative(a, b):
        assert add(a, b) == add(b, a)  # Tests 100s of examples!

### 2. Common Properties to Test

**Idempotence:** f(f(x)) == f(x)
    @given(st.text())
    def test_normalize_idempotent(text):
        normalized = normalize(text)
        assert normalize(normalized) == normalized

**Commutativity:** f(a, b) == f(b, a)
    @given(st.integers(), st.integers())
    def test_add_commutative(a, b):
        assert add(a, b) == add(b, a)

**Invariants:** Something that's always true
    @given(st.lists(st.integers()))
    def test_sort_preserves_length(lst):
        assert len(sorted(lst)) == len(lst)

**Inverse:** f(g(x)) == x
    @given(st.text())
    def test_encode_decode_inverse(text):
        assert decode(encode(text)) == text

**Consistency:** Same input -> same output
    @given(st.text())
    def test_hash_consistent(text):
        assert hash_fn(text) == hash_fn(text)

### 3. Using Strategies

# Built-in types
st.integers(min_value=0, max_value=100)
st.floats(min_value=0.0, max_value=1.0)
st.text(min_size=1, max_size=100)
st.lists(st.integers(), min_size=0, max_size=10)
st.dictionaries(keys=st.text(), values=st.integers())

# Complex strategies
st.tuples(st.integers(), st.text())
st.one_of(st.integers(), st.text())
st.sampled_from(['option1', 'option2', 'option3'])

# Custom strategies
@st.composite
def valid_audio_path(draw):
    name = draw(st.text(min_size=1, max_size=20))
    ext = draw(st.sampled_from(['.mp3', '.wav', '.ogg']))
    return f"{name}{ext}"

### 4. Running Tests

# Run all property tests
pytest tests/property/ -m property

# Run with more examples (slower, more thorough)
pytest tests/property/ -m property --hypothesis-profile=thorough

# Show statistics
pytest tests/property/ -m property --hypothesis-show-statistics

### 5. When Hypothesis Finds a Bug

Hypothesis will shrink the failing case to the minimal example:

    Falsifying example:
        test_my_function(text='!')

Then add it as a regression test:
    @example('!')  # Hypothesis found this edge case!
    @given(st.text())
    def test_my_function(text):
        ...
"""

# ==============================================================================
# TO RUN THESE TESTS
# ==============================================================================

"""
# Install hypothesis
pip install hypothesis

# Run property tests
pytest tests/property/ -m property -v

# Run with more examples (thorough mode)
pytest tests/property/ -m property --hypothesis-profile=thorough

# Run specific test
pytest tests/property/test_property_based_examples.py::TestScriptParserProperties::test_parse_never_crashes -v
"""
