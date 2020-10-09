from __future__ import absolute_import

import struct
import sys

from .common import PY2, BytesIO, string_types

if PY2:
    MAX_EXTRACT_VERSION = 63
    from zipfile import (
        BadZipfile as BadZipFile,
        ZipExtFile,
        ZipInfo,
        _CD_COMMENT_LENGTH,
        _CD_EXTRA_FIELD_LENGTH,
        _CD_FILENAME_LENGTH,
        _CD_LOCAL_HEADER_OFFSET,
        _CD_SIGNATURE,
        _ECD_LOCATION,
        _ECD_OFFSET,
        _ECD_SIGNATURE,
        _ECD_SIZE,
        _EndRecData,
        _FH_EXTRA_FIELD_LENGTH,
        _FH_FILENAME_LENGTH,
        _FH_SIGNATURE,
        sizeCentralDir,
        sizeEndCentDir64,
        sizeEndCentDir64Locator,
        sizeFileHeader,
        stringCentralDir,
        stringEndArchive64,
        stringFileHeader,
        structCentralDir,
        structFileHeader,
    )
else:
    from zipfile import (
        BadZipFile,
        MAX_EXTRACT_VERSION,
        ZipExtFile,
        ZipInfo,
        _CD_COMMENT_LENGTH,
        _CD_EXTRA_FIELD_LENGTH,
        _CD_FILENAME_LENGTH,
        _CD_LOCAL_HEADER_OFFSET,
        _CD_SIGNATURE,
        _ECD_LOCATION,
        _ECD_OFFSET,
        _ECD_SIGNATURE,
        _ECD_SIZE,
        _EndRecData,
        _FH_EXTRA_FIELD_LENGTH,
        _FH_FILENAME_LENGTH,
        _FH_SIGNATURE,
        sizeCentralDir,
        sizeEndCentDir64,
        sizeEndCentDir64Locator,
        sizeFileHeader,
        stringCentralDir,
        stringEndArchive64,
        stringFileHeader,
        structCentralDir,
        structFileHeader,
    )

from .common import TooManyFiles

_UTF8_EXTENSION_FLAG = 0x800

if sys.version_info[:2] < (2, 7):
    class _ZipExtFile(ZipExtFile):
        def __enter__(self):
            return self

        def __exit__(self, *a, **kw):
            self.close()


class LeanZipFile(object):
    """ A limited but memory efficient zipfile reader.

    This class has 2 main features:

        * the list of archives is not created explicitly at construction
          time.
        * it will raise an error when iterating over archives with more
          than a given number of members.

    The stdlib ZipFile class creates a list of all the archives in the
    constructor. This may cause issues in situations where you don't want
    to use too much memory, or when you need to handle arbitrary zip files
    (e.g. in a server).
    """
    def __init__(self, filename, max_file_count=None):
        """ Creates a new LeanZipFile instance

        Parameters
        ----------
        filename: str
            Zipfile path
        max_file_count: int or None
            the zipfile has more members than max_file_count, a
            TooManyFiles exception will be raised when accessing members
            beyond this limit. A value of None disable ths limit.
        """
        self.filename = filename
        self.fp = open(filename, 'rb')
        self.max_file_count = max_file_count

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        fp = self.fp
        self.fp = None
        if fp is not None:
            fp.close()

    def get_zip_infos(self, *filenames):
        """Read in the table of contents for the ZIP file."""
        fp = self.fp
        max_file_count = self.max_file_count

        if not fp:
            raise RuntimeError(
                "Attempt to read ZIP archive that was already closed")

        filenames = set(filenames)
        if len(filenames) == 0:
            return

        try:
            endrec = _EndRecData(fp)
        except OSError:
            raise BadZipFile("File is not a zip file")
        if not endrec:
            raise BadZipFile("File is not a zip file")

        size_cd = endrec[_ECD_SIZE]             # bytes in central directory
        offset_cd = endrec[_ECD_OFFSET]         # offset of central directory

        # "concat" is zero, unless zip was concatenated to another file
        concat = endrec[_ECD_LOCATION] - size_cd - offset_cd
        if endrec[_ECD_SIGNATURE] == stringEndArchive64:
            # If Zip64 extension structures are present, account for them
            concat -= (sizeEndCentDir64 + sizeEndCentDir64Locator)

        # start_dir:  Position of start of central directory
        start_dir = offset_cd + concat
        fp.seek(start_dir, 0)
        data = fp.read(size_cd)
        fp = BytesIO(data)
        total = 0
        file_count = 0
        while total < size_cd:
            centdir = fp.read(sizeCentralDir)
            if len(centdir) != sizeCentralDir:
                raise BadZipFile("Truncated central directory")
            centdir = struct.unpack(structCentralDir, centdir)
            if centdir[_CD_SIGNATURE] != stringCentralDir:
                raise BadZipFile("Bad magic number for central directory")
            filename = fp.read(centdir[_CD_FILENAME_LENGTH])
            flags = centdir[5]
            if flags & _UTF8_EXTENSION_FLAG:
                # UTF-8 file names extension
                filename = filename.decode('utf-8')
            else:
                # Historical ZIP filename encoding
                filename = filename.decode('cp437')
            # Create ZipInfo instance to store file information
            x = ZipInfo(filename)
            x.extra = fp.read(centdir[_CD_EXTRA_FIELD_LENGTH])
            x.comment = fp.read(centdir[_CD_COMMENT_LENGTH])
            x.header_offset = centdir[_CD_LOCAL_HEADER_OFFSET]
            (x.create_version, x.create_system, x.extract_version, x.reserved,
             x.flag_bits, x.compress_type, t, d,
             x.CRC, x.compress_size, x.file_size) = centdir[1:12]
            if x.extract_version > MAX_EXTRACT_VERSION:
                raise NotImplementedError("zip file version %.1f" %
                                          (x.extract_version / 10))
            x.volume, x.internal_attr, x.external_attr = centdir[15:18]
            # Convert date/time code to (year, month, day, hour, min, sec)
            x._raw_time = t
            x.date_time = ((d >> 9) + 1980, (d >> 5) & 0xF, d & 0x1F,
                           t >> 11, (t >> 5) & 0x3F, (t & 0x1F) * 2)

            x._decodeExtra()
            x.header_offset = x.header_offset + concat

            # update total bytes read from central directory
            total = (total + sizeCentralDir + centdir[_CD_FILENAME_LENGTH]
                     + centdir[_CD_EXTRA_FIELD_LENGTH]
                     + centdir[_CD_COMMENT_LENGTH])

            file_count += 1
            if max_file_count is not None and file_count > max_file_count:
                raise TooManyFiles('Too many files in egg')

            if x.filename in filenames:
                filenames.discard(x.filename)
                yield x

            if len(filenames) == 0:
                return

    def open(self, zinfo):
        zef_file = self.fp

        if not zef_file:
            raise RuntimeError(
                "Attempt to read ZIP archive that was already closed")

        zef_file.seek(zinfo.header_offset, 0)

        # Skip the file header:
        fheader = zef_file.read(sizeFileHeader)
        if len(fheader) != sizeFileHeader:
            raise BadZipFile("Truncated file header")
        fheader = struct.unpack(structFileHeader, fheader)
        if fheader[_FH_SIGNATURE] != stringFileHeader:
            raise BadZipFile("Bad magic number for file header")

        fname = zef_file.read(fheader[_FH_FILENAME_LENGTH])
        if fheader[_FH_EXTRA_FIELD_LENGTH]:
            zef_file.read(fheader[_FH_EXTRA_FIELD_LENGTH])

        if zinfo.flag_bits & 0x20:
            # Zip 2.7: compressed patched data
            raise NotImplementedError("compressed patched data (flag bit 5)")

        if zinfo.flag_bits & 0x40:
            # strong encryption
            raise NotImplementedError("strong encryption (flag bit 6)")

        if zinfo.flag_bits & _UTF8_EXTENSION_FLAG:
            # UTF-8 filename
            fname_str = fname.decode("utf-8")
        else:
            fname_str = fname.decode("cp437")

        if fname_str != zinfo.orig_filename:
            raise BadZipFile(
                'File name in directory %r and header %r differ.'
                % (zinfo.orig_filename, fname))

        if sys.version_info[:2] < (2, 7):
            return _ZipExtFile(zef_file, zinfo)
        elif sys.version_info[:2] < (3, 4) and sys.platform == 'win32':
                return ZipExtFile(zef_file, 'r', zinfo)
        else:
            return ZipExtFile(zef_file, 'r', zinfo, None, close_fileobj=False)

    def read(self, zinfo_or_name):
        """Return file bytes (as a string) for the given ZipInfo object or
        archive name..

        Parameters
        ----------
        zinfo_or_name: str
            If a string, understood as the full path to the archive name.
            Otherwise, is interpreted as a ZipInfo instance.

        Note
        ----
        Will raise an error if more than one member is found with the
        given name.
        """
        if isinstance(zinfo_or_name, string_types):
            candidates = list(self.get_zip_infos(zinfo_or_name))
            if len(candidates) < 1:
                msg = "There is no item named {0!r} found in the archive"
                raise KeyError(msg.format(zinfo_or_name))
            elif len(candidates) > 1:
                msg = ("There is more than one item named {0!r} found in "
                       "the archive.")
                raise ValueError(msg.format(zinfo_or_name))
            zinfo = candidates[0]
        else:
            zinfo = zinfo_or_name
        with self.open(zinfo) as fp:
            return fp.read()
