import os
import shutil
from typing import Optional
from types import TracebackType


class TempDistributionPath:
    """Context manager for distribution path."""

    def __init__(self, archive_path: str) -> None:
        self.archive = archive_path
        self.path = os.path.join(
            os.path.dirname(archive_path), '__pypackages__'
        )

    def __enter__(self) -> str:
        shutil.unpack_archive(self.archive, self.path)
        return os.path.join(self.path)

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        print(type(exc_type), type(exc_value), type(traceback))
        shutil.rmtree(self.path)
