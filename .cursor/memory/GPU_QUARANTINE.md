Title: GPU Quarantine

Summary: Tests marked @pytest.mark.gpu are skipped by default across local and CI unless PY_ENABLE_GPU_TESTS=1. Mutmut excludes GPU tests by default for determinism. Use scripts/test_env_example.* to set env vars.

Action: When generating or modifying tests, always mark device-dependent tests with @pytest.mark.gpu and document any CUDA/driver assumptions.

