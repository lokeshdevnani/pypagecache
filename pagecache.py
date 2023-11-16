import math
import os
from dataclasses import dataclass
from mmap import PAGESIZE

from pypagecache.syscallwrapperutils import SyscallWrapperUtils


@dataclass
class PyPageCacheStats:
    filesize: int
    pagesize: int
    cached_pages: int
    total_pages: int

    def __init__(self, filesize, pagesize, cached_pages):
        self.filesize = filesize
        self.pagesize = pagesize
        self.cached_pages = cached_pages
        self.total_pages = math.ceil(float(filesize) / pagesize)

    def cached_percent(self):
        return (self.cached_pages * 100 / self.total_pages) if self.total_pages > 0 else 0.0

    def __str__(self):
        return f"Page cache stats: [{self.cached_pages}/{self.total_pages}] ({self.cached_percent()}%)"

    @staticmethod
    def empty(pagesize):
        return PyPageCacheStats(0, pagesize, 0)

    @staticmethod
    def combine(stats_list: list['PyPageCacheStats']) -> 'PyPageCacheStats' | None:
        if len(stats_list) == 0:
            return None

        agg = PyPageCacheStats.empty(stats_list[0].pagesize)
        for stats in stats_list:
            agg.filesize += stats.filesize
            agg.cached_pages += stats.cached_pages
            agg.total_pages += stats.total_pages
        return agg


class PyPageCache:
    def __init__(self, path):
        self.path = path

    def touch(self):
        return self.run("touch")

    def evict(self):
        return self.run("evict")

    def stats(self):
        return self.run("stats")

    def run(self, operation):
        if os.path.isfile(self.path):
            return self._run(self.path, operation)
        elif os.path.isdir(self.path):
            return self._run_directory(self.path, operation)
        elif not os.path.exists(self.path):
            raise ValueError(f"Invalid path: {self.path}")
        else:
            raise ValueError(f"Unsupported object type: {self.path}")

    def _run_directory(self, path, operation):
        stats = [self._run(filepath, operation) for filepath in self._directory_iterator(path)]
        return PyPageCacheStats.combine(stats)

    def _run(self, filepath, operation) -> PyPageCacheStats:
        syscall_utils = SyscallWrapperUtils()

        with open(filepath, "r") as fd:
            filesize = os.path.getsize(filepath)

            if filesize == 0:
                return PyPageCacheStats.empty(PAGESIZE)

            faddr = syscall_utils.mmap_wrapper(fd, filepath, filesize)

            if faddr is None:
                return None

            if operation == "touch":
                syscall_utils.touch_pages(faddr, filesize)
            elif operation == "evict":
                syscall_utils.evict_pages_wrapper(faddr, filesize)
            elif operation == "stats":
                pass  # do nothing
            else:
                raise ValueError(f"Unsupported operation: {operation}")

            cached_pages = syscall_utils.mincore_wrapper(faddr, filesize)
            syscall_utils.munmap(faddr, filesize)

            return PyPageCacheStats(filesize=filesize, pagesize=PAGESIZE, cached_pages=cached_pages)

    def _directory_iterator(self, dirpath):
        for root, dirs, files in os.walk(dirpath):
            for file in files:
                yield os.path.join(root, file)
