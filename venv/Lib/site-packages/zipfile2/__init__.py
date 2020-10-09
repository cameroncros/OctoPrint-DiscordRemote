from __future__ import absolute_import

try:
    from ._version import (full_version as __version__,
                           git_revision as __git_revision__,
                           is_released as __is_released__)
except ImportError:
    __version__ = __git_revision__ = "no-built"
    __is_released__ = False

from .common import TooManyFiles
from ._zipfile import (
    PERMS_PRESERVE_NONE, PERMS_PRESERVE_SAFE, PERMS_PRESERVE_ALL, ZipFile
)
from ._lean_zipfile import LeanZipFile
from zipfile import (
    ZIP64_LIMIT, ZIP_DEFLATED, ZIP_FILECOUNT_LIMIT, ZIP_MAX_COMMENT,
    ZIP_STORED,
)

__all__ = [
    "__git_revision__", "__is_released__", "__version__", "LeanZipFile",
    "TooManyFiles", "ZipFile", "PERMS_PRESERVE_NONE", "PERMS_PRESERVE_SAFE",
    "PERMS_PRESERVE_ALL", "ZIP64_LIMIT", "ZIP_DEFLATED", "ZIP_FILECOUNT_LIMIT",
    "ZIP_MAX_COMMENT", "ZIP_STORED",
]
