"""Test suite initialization with Hypothesis profile configuration."""

from __future__ import annotations

from hypothesis import HealthCheck, settings
from hypothesis import strategies as st  # noqa: F401  (re-export if needed)


settings.register_profile(
    "ci",
    settings(
        max_examples=100,
        deadline=None,
        suppress_health_check=(HealthCheck.too_slow,),
    ),
)

settings.load_profile("ci")
