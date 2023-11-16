import ctypes
import sys
from ctypes import c_void_p, c_ssize_t, c_size_t, c_int, POINTER, c_ubyte, cdll, get_errno, cast
from mmap import PROT_READ, MAP_SHARED, PAGESIZE


class SyscallWrapperUtils:
    MAP_FAILED = c_void_p(-1)
    MS_INVALIDATE = 2
    POSIX_FADV_DONTNEED = 4

    def __init__(self):
        self.c_off_t = c_ssize_t
        self._initialize_functions()

    def _initialize_functions(self):
        libc = self._load_libc()

        self.mmap = self._initialize_function(libc.mmap, [c_void_p, c_size_t, c_int, c_int, self.c_off_t], c_void_p)
        self.munmap = self._initialize_function(libc.munmap, [c_void_p, c_size_t], c_void_p)
        self.mincore = self._initialize_function(libc.mincore, [c_void_p, c_size_t, POINTER(c_ubyte)], c_int)

        if hasattr(libc, 'posix_fadvise'):
            self.posix_fadvise = self._initialize_function(libc.posix_fadvise, [c_int, c_size_t, c_int, c_int], c_int)
        elif hasattr(libc, 'msync'):
            self.msync = self._initialize_function(libc.msync, [c_void_p, c_size_t, c_int], ctypes.c_int)
        else:
            raise OSError("msync/posix_fadvise not supported")

    def _load_libc(self):
        if sys.platform.startswith('linux'):
            return cdll.LoadLibrary("libc.so.6")
        elif sys.platform == 'darwin':
            return cdll.LoadLibrary("libSystem.dylib")
        else:
            raise OSError("Unsupported platform")

    def _initialize_function(self, func, argtypes, restype):
        func.argtypes = argtypes
        func.restype = restype
        return func

    def evict_pages_wrapper(self, faddr, filesize):
        if hasattr(self, 'posix_fadvise'):
            rv = self.posix_fadvise(faddr, 0, filesize, self.POSIX_FADV_DONTNEED)
        elif hasattr(self, 'msync'):
            rv = self.msync(faddr, filesize, self.MS_INVALIDATE)
        else:
            raise OSError("posix_fadvise/msync not supported in platform libc")
        if rv == -1:
            print(f"msync/posix_fadvise failed: {faddr}, {filesize}: {get_errno()}")

    def mmap_wrapper(self, fd, filename, filesize):
        faddr = self.mmap(0, filesize, PROT_READ, MAP_SHARED, fd.fileno(), 0)
        if faddr == self.MAP_FAILED:
            print(f"Failed to mmap {filename} (errno: {get_errno()})")
            return None
        return faddr

    def mincore_wrapper(self, faddr, filesize):
        vec_size = self.num_pages(filesize)
        vec = (c_ubyte * vec_size)()
        rv = self.mincore(faddr, filesize, cast(vec, POINTER(c_ubyte)))
        if rv == -1:
            print(f"mincore failed: {faddr}, {filesize}: {get_errno()}")
        return sum(x & 1 for x in vec)

    def num_pages(self, filesize):
        return (filesize + PAGESIZE - 1) // PAGESIZE

    def touch_pages(self, faddr, filesize):
        mem = ctypes.cast(faddr, ctypes.POINTER(ctypes.c_byte))
        page_count = self.num_pages(filesize)
        devnull = 0
        for i in range(page_count):
            byte_we_dont_care_about = mem[i * PAGESIZE]
            devnull += byte_we_dont_care_about
