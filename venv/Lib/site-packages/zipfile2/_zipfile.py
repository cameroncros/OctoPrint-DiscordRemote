from __future__ import absolute_import

import errno
import os
import shutil
import stat
import string
import sys
import time
import zipfile

from .common import text_type


IS_ZIPFILE_OLD_STYLE_CLASS = sys.version_info[:3] < (2, 7, 4)
ZIP_SOFTLINK_ATTRIBUTE_MAGIC = 0xA1ED0000

# Enum choices for Zipfile.extractall preserve_permissions argument
PERMS_PRESERVE_NONE, PERMS_PRESERVE_SAFE, PERMS_PRESERVE_ALL = range(3)

# Use octal as it is the convention used in zipinfo.c (as found in e.g. apt-get
# source unzip)
_UNX_IFMT   = 0o170000  # Unix file type mask
_UNX_IFLNK  = 0o120000  # Unix symbolic link


def is_zipinfo_symlink(zip_info):
    """Return True if the given zip_info instance refers to a symbolic link."""
    mode = zip_info.external_attr >> 16
    return (mode & _UNX_IFMT) == _UNX_IFLNK


class ZipFile(zipfile.ZipFile):
    """
    A ZipFile implementation that knows how to extract soft links and allows
    overriding target destination.

    This also support context management on 2.6.
    """
    def __init__(self, file, mode='r', compression=zipfile.ZIP_STORED,
                 allowZip64=True, low_level=False):
        """ Open the ZIP file.

        Parameters
        ----------
        file: str
            Filename
        mode: str
            'r' for read, 'w' for write, 'a' for append
        compression: int
            Which compression method to use.
        low_level: bool
            If False, will raise an error when adding an already existing
            archive.
        """
        if IS_ZIPFILE_OLD_STYLE_CLASS:
            zipfile.ZipFile.__init__(self, file, mode, compression, allowZip64)
        else:
            super(ZipFile, self).__init__(file, mode, compression, allowZip64)

        self.low_level = low_level

        # Set of filenames currently in file
        members = self.namelist()
        self._filenames_set = set(members)
        if len(self._filenames_set) != len(members) and not self.low_level:
            msg = ("Duplicate members in zip archive detected. If you "
                   "want to support this, use low_level=True.")
            raise ValueError(msg)

    def add_tree(self, directory, include_top=False):
        """ Zip the given directory into this archive, by walking into it.

        The archive names will be relative to the directory, e.g. for::

            <directory>/foo.txt
            <directory>/bar/foo.txt

        doing add_tree(<directory>) will give you a zipfile with the content::

            foo.txt
            bar/foo.txt
        """
        if include_top:
            base = os.path.basename(directory)
        else:
            base = "."

        for root, dirs, files in os.walk(directory):
            entries = [os.path.join(root, entry) for entry in dirs + files]
            for entry in entries:
                arcname = os.path.join(base, os.path.relpath(entry, directory))
                self.write(entry, arcname)

    def extract(self, member, path=None, pwd=None,
                preserve_permissions=PERMS_PRESERVE_NONE):
        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()

        return self._extract_member(member, path, pwd, preserve_permissions)

    def extractall(self, path=None, members=None, pwd=None,
                   preserve_permissions=PERMS_PRESERVE_NONE):
        """ Extract all members from the archive to the current working
        directory.

        Parameters
        -----------
        path: str
            path specifies a different directory to extract to.
        members: list
            is optional and must be a subset of the list returned by
            namelist().
        preserve_permissions: int
            controls whether permissions of zipped files are preserved or
            not. Default is PERMS_PRESERVE_NONE - do not preserve any
            permissions. Other options are to preserve safe subset of
            permissions PERMS_PRESERVE_SAFE or all permissions
            PERMS_PRESERVE_ALL.
        """
        if members is None:
            members = self.namelist()

        for zipinfo in members:
            self.extract(zipinfo, path, pwd, preserve_permissions)

    def extract_to(self, member, destination, path=None, pwd=None,
                   preserve_permissions=PERMS_PRESERVE_NONE):
        if not isinstance(member, zipfile.ZipInfo):
            member = self.getinfo(member)

        if path is None:
            path = os.getcwd()

        return self._extract_member_to(member, destination, path, pwd,
                                       preserve_permissions)

    def write(self, filename, arcname=None, compress_type=None):
        if arcname is None:
            arcname = filename
        st = os.lstat(filename)

        arcname = self._normalize_arcname(arcname)

        if stat.S_ISDIR(st.st_mode):
            arcname += '/'

        self._ensure_uniqueness(arcname)
        if stat.S_ISLNK(st.st_mode):
            mtime = time.localtime(st.st_mtime)
            date_time = mtime[0:6]

            zip_info = zipfile.ZipInfo(arcname, date_time)
            zip_info.create_system = 3
            zip_info.external_attr = ZIP_SOFTLINK_ATTRIBUTE_MAGIC
            self.writestr(zip_info, os.readlink(filename))
        else:
            if IS_ZIPFILE_OLD_STYLE_CLASS:
                zipfile.ZipFile.write(self, filename, arcname, compress_type)
            else:
                super(ZipFile, self).write(filename, arcname, compress_type)
            self._filenames_set.add(arcname)

    def writestr(self, zinfo_or_arcname, bytes, compress_type=None):
        if not isinstance(zinfo_or_arcname, zipfile.ZipInfo):
            arcname = self._normalize_arcname(zinfo_or_arcname)
        else:
            arcname = zinfo_or_arcname.filename

        self._ensure_uniqueness(arcname)

        self._filenames_set.add(arcname)
        if IS_ZIPFILE_OLD_STYLE_CLASS:
            zipfile.ZipFile.writestr(self, zinfo_or_arcname, bytes)
        else:
            super(ZipFile, self).writestr(zinfo_or_arcname, bytes,
                                          compress_type)

    # Overriden so that ZipFile.extract* support softlink
    def _extract_member(self, member, targetpath, pwd, preserve_permissions):
        return self._extract_member_to(member, member.filename,
                                       targetpath, pwd, preserve_permissions)

    def _extract_symlink(self, member, link_name, pwd=None):
        source = self.read(member).decode("utf8")
        if os.path.lexists(link_name):
            os.unlink(link_name)
        os.symlink(source, link_name)
        return link_name

    # This is mostly copied from the stdlib zipfile.ZipFile._extract_member,
    # extended to allow soft link support. This needed copying to allow arcname
    # to not be based on ZipInfo.arcname
    def _extract_member_to(self, member, arcname, targetpath, pwd,
                           preserve_permissions):
        """Extract the ZipInfo object 'member' to a physical
           file on the path targetpath.
        """
        # build the destination pathname, replacing
        # forward slashes to platform specific separators.
        arcname = arcname.replace('/', os.path.sep)

        if os.path.altsep:
            arcname = arcname.replace(os.path.altsep, os.path.sep)
        # interpret absolute pathname as relative, remove drive letter or
        # UNC path, redundant separators, "." and ".." components.
        arcname = os.path.splitdrive(arcname)[1]
        arcname = os.path.sep.join(x for x in arcname.split(os.path.sep)
                                   if x not in ('', os.path.curdir,
                                                os.path.pardir))
        if os.path.sep == '\\':
            # filter illegal characters on Windows
            illegal = ':<>|"?*'
            if isinstance(arcname, text_type):
                table = dict((ord(c), ord('_')) for c in illegal)
            else:
                table = string.maketrans(illegal, '_' * len(illegal))
            arcname = arcname.translate(table)
            # remove trailing dots
            arcname = (x.rstrip('.') for x in arcname.split(os.path.sep))
            arcname = os.path.sep.join(x for x in arcname if x)

        targetpath = os.path.join(targetpath, arcname)
        targetpath = os.path.normpath(targetpath)

        # Create all upper directories if necessary.
        upperdirs = os.path.dirname(targetpath)
        if upperdirs and not os.path.exists(upperdirs):
            os.makedirs(upperdirs)

        if member.filename[-1] == '/':
            if not os.path.isdir(targetpath):
                os.mkdir(targetpath)
            return targetpath
        elif is_zipinfo_symlink(member):
            return self._extract_symlink(member, targetpath, pwd)
        else:
            source = self.open(member, pwd=pwd)
            try:
                _unlink_if_exists(targetpath)
                with open(targetpath, "wb") as target:
                    shutil.copyfileobj(source, target)
            finally:
                source.close()

            if preserve_permissions in (PERMS_PRESERVE_SAFE, PERMS_PRESERVE_ALL):
                if preserve_permissions == PERMS_PRESERVE_ALL:
                    # preserve bits 0-11: sugrwxrwxrwx, this include
                    # sticky bit, uid bit, gid bit
                    mode = member.external_attr >> 16 & 0xFFF
                elif PERMS_PRESERVE_SAFE:
                    # preserve bits 0-8 only: rwxrwxrwx
                    mode = member.external_attr >> 16 & 0x1FF
                os.chmod(targetpath, mode)

            return targetpath

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _ensure_uniqueness(self, arcname):
        if not self.low_level and arcname in self._filenames_set:
            msg = "{0!r} is already in archive".format(arcname)
            raise ValueError(msg)

    def _normalize_arcname(self, arcname):
        arcname = os.path.normpath(os.path.splitdrive(arcname)[1])
        while arcname[0] in (os.sep, os.altsep):
            arcname = arcname[1:]
        # This is used to ensure paths in generated ZIP files always use
        # forward slashes as the directory separator, as required by the
        # ZIP format specification.
        if os.sep != "/" and os.sep in arcname:
            arcname = arcname.replace(os.sep, "/")

        return arcname


def _unlink_if_exists(p):
    try:
        os.unlink(p)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
