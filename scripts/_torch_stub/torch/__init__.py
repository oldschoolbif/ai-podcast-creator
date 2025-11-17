# Minimal Torch stub for environments without PyTorch, used only to allow tests
class _CudaProps:
    def __init__(self, total_memory=8 * (1024**3)):
        self.total_memory = total_memory


class _CudaBackendMatmul:
    def __init__(self):
        self.allow_tf32 = False


class _CudnnBackend:
    def __init__(self):
        self.enabled = True
        self.benchmark = True
        self.allow_tf32 = False


class _CudaBackend:
    def __init__(self):
        self.matmul = _CudaBackendMatmul()


class _Backends:
    def __init__(self):
        self.cudnn = _CudnnBackend()
        self.cuda = _CudaBackend()


class _Cuda:
    def __init__(self):
        self._available = False
        self._device_name = "Stub GPU"
        self._device_count = 1
        self._props = _CudaProps()

    def is_available(self):
        return self._available

    def get_device_name(self, idx):
        return self._device_name

    def get_device_properties(self, idx):
        return self._props

    def get_device_capability(self, idx=0):
        # Return Ampere-like by default
        return (8, 0) if self._available else (0, 0)

    def empty_cache(self):
        return None

    def synchronize(self):
        return None

    def memory_allocated(self, idx=0):
        return 0

    def memory_reserved(self, idx=0):
        return 0

    def set_device(self, idx):
        return None

    def device_count(self):
        return self._device_count


cuda = _Cuda()
backends = _Backends()


class _Version:
    cuda = "stub"


version = _Version()


def device(name):
    return f"device({name})"

def load(*args, **kwargs):
    # Minimal stub: return a simple object
    return object()

class inference_mode:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False


