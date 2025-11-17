Title: Hardware Acceleration Profile

Summary: Cursor may use up to 80–90% of CPU cores and GPU resources to expedite testing and builds. Controlled by PY_PARALLEL, PY_GPU_MAX_LOAD, and PY_MEMORY_LIMIT_FRACTION. Safe fallback at 50% if thermal or resource alerts occur.

Action: When generating new workflows or configs, default to parallel test execution and GPU acceleration unless explicitly disabled.

