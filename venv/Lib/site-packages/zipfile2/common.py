import sys
import zipfile


PY2 = sys.version_info[0] == 2

if PY2:
    import cStringIO
    string_types = basestring,
    text_type = unicode
    BytesIO = cStringIO.StringIO
else:
    import io
    string_types = str,
    text_type = str
    BytesIO = io.BytesIO


class TooManyFiles(zipfile.BadZipfile):
    pass
