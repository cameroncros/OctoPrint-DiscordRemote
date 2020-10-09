from __future__ import absolute_import

import errno
import hashlib
import os
import os.path
import shutil
import stat
import sys
import tempfile
import zipfile

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from zipfile2 import (
    PERMS_PRESERVE_SAFE, PERMS_PRESERVE_ALL, ZipFile
)

from ..common import PY2, string_types
from .common import (
    NOSE_EGG, VTK_EGG, ZIP_WITH_DIRECTORY_SOFTLINK, ZIP_WITH_SOFTLINK,
    ZIP_WITH_PERMISSIONS, ZIP_WITH_SOFTLINK_AND_PERMISSIONS
)

if PY2:
    import StringIO
    BytesIO = StringIO.StringIO
else:
    import io
    BytesIO = io.BytesIO

SUPPORT_SYMLINK = hasattr(os, "symlink")

HERE = os.path.dirname(__file__)


def handle_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        # change the file to be readable,writable,executable: 0777
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        # retry
        func(path)
    else:
        raise


def list_files(top):
    paths = []
    for root, dirs, files in os.walk(top):
        for f in files:
            paths.append(os.path.join(os.path.relpath(root, top), f))
    return paths


def compute_md5(path):
    m = hashlib.md5()
    block_size = 2 ** 16

    def _compute_checksum(fp):
        while True:
            data = fp.read(block_size)
            m.update(data)
            if len(data) < block_size:
                break
        return m.hexdigest()

    if isinstance(path, string_types):
        with open(path, "rb") as fp:
            return _compute_checksum(fp)
    else:
        return _compute_checksum(path)


def create_broken_symlink(link):
    d = os.path.dirname(link)
    os.makedirs(d)
    os.symlink(os.path.join(d, "nono_le_petit_robot"), link)


class TestZipFile(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.tempdir2 = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir2)
        shutil.rmtree(self.tempdir)

    if PY2:
        def assertCountEqual(self, first, second, msg=None):
            return self.assertItemsEqual(first, second, msg)

    def test_simple(self):
        # Given
        path = NOSE_EGG
        r_paths = [
            os.path.join("EGG-INFO", "entry_points.txt"),
            os.path.join("EGG-INFO", "PKG-INFO"),
            os.path.join("EGG-INFO", "spec", "depend"),
            os.path.join("EGG-INFO", "spec", "summary"),
            os.path.join("EGG-INFO", "usr", "share", "man", "man1",
                         "nosetests.1"),
        ]

        # When
        with ZipFile(path) as zp:
            zp.extractall(self.tempdir)
        paths = list_files(self.tempdir)

        # Then
        self.assertCountEqual(paths, r_paths)

    def test_extract(self):
        # Given
        path = NOSE_EGG
        arcname = "EGG-INFO/PKG-INFO"

        # When
        with ZipFile(path) as zp:
            zp.extract(arcname, self.tempdir)
        self.assertTrue(os.path.exists(os.path.join(self.tempdir, arcname)))

    def test_extract_to(self):
        # Given
        path = NOSE_EGG
        arcname = "EGG-INFO/PKG-INFO"

        # When
        with ZipFile(path) as zp:
            zp.extract_to(arcname, "FOO", self.tempdir)
            extracted_data = zp.read(arcname)
        self.assertTrue(os.path.exists(os.path.join(self.tempdir, "FOO")))
        self.assertEqual(compute_md5(os.path.join(self.tempdir, "FOO")),
                         compute_md5(BytesIO(extracted_data)))
        self.assertFalse(os.path.exists(os.path.join(self.tempdir, "EGG-INFO",
                                                     "PKG-INFO")))

    @unittest.skipIf(not SUPPORT_SYMLINK,
                     "this platform does not support symlink")
    def test_softlink(self):
        # Given
        path = ZIP_WITH_SOFTLINK

        # When/Then
        with ZipFile(path) as zp:
            zp.extractall(self.tempdir)
        paths = list_files(self.tempdir)

        self.assertCountEqual(paths, [os.path.join("lib", "foo.so.1.3"),
                                      os.path.join("lib", "foo.so")])
        self.assertTrue(os.path.islink(
            os.path.join(self.tempdir, "lib", "foo.so"))
        )

    @unittest.skipIf(not SUPPORT_SYMLINK,
                     "this platform does not support symlink")
    def test_directory_softlink(self):
        # Given
        path = ZIP_WITH_DIRECTORY_SOFTLINK

        directory_link = os.path.join("lib", "foo")
        r_directory_link = os.path.join(self.tempdir, directory_link)

        r_paths = (
            os.path.join("lib", "foo-1", "foo.so.1.3"),
            os.path.join("lib", "foo-1", "foo.so"),
        )

        # When
        with ZipFile(path) as zp:
            zp.extractall(self.tempdir)

        # Then
        paths = list_files(self.tempdir)
        self.assertCountEqual(paths, r_paths)
        self.assertTrue(os.path.islink(r_directory_link))
        target = os.readlink(r_directory_link)
        self.assertEqual(target, "foo-1")

    @unittest.skipIf(not SUPPORT_SYMLINK,
                     "this platform does not support symlink")
    def test_softlink_with_broken_entry(self):
        self.maxDiff = None

        # Given
        path = VTK_EGG
        expected_files = [
            os.path.join('EGG-INFO', 'PKG-INFO'),
            os.path.join('EGG-INFO', 'inst', 'targets.dat'),
            os.path.join('EGG-INFO', 'inst', 'files_to_install.txt'),
            os.path.join('EGG-INFO', 'usr', 'lib', 'vtk-5.10',
                         'libvtkViews.so.5.10.1'),
            os.path.join('EGG-INFO', 'usr', 'lib', 'vtk-5.10',
                         'libvtkViews.so.5.10'),
            os.path.join('EGG-INFO', 'usr', 'lib', 'vtk-5.10',
                         'libvtkViews.so'),
            os.path.join('EGG-INFO', 'spec', 'lib-provide'),
            os.path.join('EGG-INFO', 'spec', 'depend'),
            os.path.join('EGG-INFO', 'spec', 'lib-depend'),
            os.path.join('EGG-INFO', 'spec', 'summary'),
        ]

        existing_link = os.path.join(self.tempdir,
                                     'EGG-INFO/usr/lib/vtk-5.10/'
                                     'libvtkViews.so')
        create_broken_symlink(existing_link)

        # When
        with ZipFile(path) as zp:
            zp.extractall(self.tempdir)
        files = list_files(self.tempdir)

        # Then
        self.assertCountEqual(files, expected_files)
        path = os.path.join(self.tempdir,
                            "EGG-INFO/usr/lib/vtk-5.10/libvtkViews.so")
        self.assertTrue(os.path.islink(path))

    def test_multiple_archives_write(self):
        # Given
        zipfile = os.path.join(self.tempdir, "foo.zip")
        to = os.path.join(self.tempdir, "to")
        filename = os.path.relpath(__file__, os.getcwd())

        # When
        with ZipFile(zipfile, "w") as zp:
            zp.write(filename)
            with self.assertRaises(ValueError):
                zp.write(filename)

        with ZipFile(zipfile) as zp:
            zp.extractall(to)

        # Then
        self.assertTrue(os.path.exists(zipfile))
        self.assertTrue(os.path.exists(os.path.join(to, filename)))

    def test_multiple_archives_writestr(self):
        # Given
        zipfile = os.path.join(self.tempdir, "foo.zip")
        target = os.path.join(self.tempdir, "file.py")

        # When
        with ZipFile(zipfile, "w") as zp:
            zp.writestr("file.py", b"data")
            with self.assertRaises(ValueError):
                zp.writestr("file.py", b"dato")

        with ZipFile(zipfile) as zp:
            new_path = zp.extract("file.py", self.tempdir)
            data = zp.read("file.py")

        # Then
        self.assertTrue(os.path.exists(zipfile))
        self.assertTrue(os.path.exists(target))
        self.assertEqual(data, b"data")
        self.assertEqual(new_path, target)

    def test_multiple_archives_writestr_write(self):
        # Given
        zipfile = os.path.join(self.tempdir, "foo.zip")
        to = os.path.join(self.tempdir, "to")
        filename = os.path.relpath(__file__, os.getcwd())
        arcname = filename

        # When
        with ZipFile(zipfile, "w") as zp:
            zp.write(filename, arcname)
            with self.assertRaises(ValueError):
                zp.writestr(arcname, b"data")

        with ZipFile(zipfile) as zp:
            zp.extractall(to)

        # Then
        self.assertTrue(os.path.exists(zipfile))
        self.assertTrue(os.path.exists(os.path.join(to, filename)))

    def test_multiple_archives_read(self):
        # Given
        zipfile = os.path.join(self.tempdir, "foo.zip")

        # When
        with ZipFile(zipfile, "w", low_level=True) as zp:
            zp.writestr("file.py", b"data")
            zp.writestr("file.py", b"dato")

        # Then
        # ensure we have indeed two members with archive name file.py
        with ZipFile(zipfile, low_level=True) as zp:
            self.assertEqual(len(zp.namelist()), 2)

        # ensure we raise an error if duplicates
        with self.assertRaises(ValueError):
            with ZipFile(zipfile) as zp:
                pass

    @unittest.skipIf(not SUPPORT_SYMLINK,
                     "this platform does not support symlink")
    def test_write_symlink_file(self):
        # Given
        zipfile = os.path.join(self.tempdir, "foo.zip")
        real_file = os.path.join(self.tempdir, "foo.txt")
        symlink = os.path.join(self.tempdir, "symlink")

        with open(real_file, "wb") as fp:
            fp.write(b"data")
        os.symlink(real_file, symlink)

        extract_dir = os.path.join(self.tempdir, "to")
        os.makedirs(extract_dir)

        r_real_file = os.path.join(extract_dir, "foo.txt")
        r_symlink = os.path.join(extract_dir, "symlink")

        # When
        with ZipFile(zipfile, "w") as zp:
            zp.write(symlink, "symlink")
            zp.write(real_file, "foo.txt")

        with ZipFile(zipfile) as zp:
            zp.extractall(extract_dir)

        # Then
        with ZipFile(zipfile) as zp:
            self.assertEqual(len(zp.namelist()), 2)
            self.assertCountEqual(zp.namelist(), ("foo.txt", "symlink"))

        self.assertFalse(os.path.islink(r_real_file))
        self.assertTrue(os.path.islink(r_symlink))
        self.assertTrue(os.readlink(r_symlink), r_real_file)

    @unittest.skipIf(not SUPPORT_SYMLINK,
                     "this platform does not support symlink")
    def test_write_symlink_directory(self):
        # Given
        zipfile = os.path.join(self.tempdir, "foo.zip")
        real_file = os.path.join(self.tempdir, "include", "foo.h")
        symlink = os.path.join(self.tempdir, "HEADERS")

        os.makedirs(os.path.dirname(real_file))
        with open(real_file, "wb") as fp:
            fp.write(b"/* header */")
        os.symlink(os.path.dirname(real_file), symlink)

        extract_dir = os.path.join(self.tempdir, "to")
        os.makedirs(extract_dir)

        r_real_file = os.path.join(extract_dir, "include", "foo.h")
        r_symlink = os.path.join(extract_dir, "HEADERS")

        # When
        with ZipFile(zipfile, "w") as zp:
            zp.write(symlink, "HEADERS")
            zp.write(real_file, "include/foo.h")

        with ZipFile(zipfile) as zp:
            zp.extractall(extract_dir)

        # Then
        with ZipFile(zipfile) as zp:
            self.assertEqual(len(zp.namelist()), 2)
            self.assertCountEqual(zp.namelist(), ("include/foo.h", "HEADERS"))

        self.assertFalse(os.path.islink(r_real_file))
        self.assertTrue(os.path.islink(r_symlink))
        self.assertTrue(os.path.isdir(r_symlink))
        self.assertTrue(os.readlink(r_symlink), r_real_file)

    def test_context_manager(self):
        # Given
        path = NOSE_EGG

        # When/Then
        with ZipFile(path) as zp:
            self.assertIsNotNone(zp.fp)

        # Then
        self.assertIsNone(zp.fp)

        # When/Then
        try:
            with ZipFile(path) as zp:
                raise ValueError("I am failing !")
        except ValueError:
            pass

        # Then
        self.assertIsNone(zp.fp)

    @unittest.skipIf(not SUPPORT_SYMLINK,
                     "this platform does not support symlink")
    def test_permissions(self):
        # Given
        path = ZIP_WITH_PERMISSIONS
        symlink = os.path.join(self.tempdir, "bin", "python")
        target = os.path.join(self.tempdir, "bin", "python2.7")
        if sys.platform == "win32":
            r_mode = 0o666
        else:
            r_mode = 0o755

        # When/Then
        with ZipFile(path) as zp:
            zp.extractall(self.tempdir,
                          preserve_permissions=PERMS_PRESERVE_SAFE)

        # Then
        self.assertTrue(os.path.exists(symlink))
        self.assertTrue(os.path.exists(target))
        self.assertEqual(stat.S_IMODE(os.stat(target).st_mode), r_mode)

    @unittest.skipIf(not SUPPORT_SYMLINK,
                     "this platform does not support symlink")
    def test_existing_symlink_replacement(self):
        # Ensure that when we overwrite an existing file with extract* methods,
        # we don't fail in the case a file already exists but is a symlink to a
        # file we don't have access to.
        self.maxDiff = None

        # Given
        path = ZIP_WITH_SOFTLINK
        some_data = b"some data"
        r_files = [
            os.path.join("lib", "foo.so.1.3"), os.path.join("lib", "foo.so")
        ]
        r_link = os.path.join(self.tempdir, "lib", "foo.so")
        r_file = os.path.join(self.tempdir, "lib", "foo.so.1.3")

        read_only_file = os.path.join(self.tempdir2, "read_only_file")

        def _create_read_only_file(read_only_file):
            with open(read_only_file, "wb") as fp:
                fp.write(some_data)

            mode = os.stat(read_only_file)[stat.ST_MODE]
            os.chmod(
                read_only_file,
                mode & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH
            )

            try:
                with open(read_only_file, "wb") as fp:
                    pass
                raise RuntimeError("Creation of RO file failed")
            except IOError as e:
                if e.errno != errno.EACCES:
                    raise

        def _create_link_to_ro(link_to_read_only_file):
            # Hack: we create a symlink toward a RO file to check the
            # destination can be overwritten
            assert not os.path.islink(link_to_read_only_file)

            os.unlink(link_to_read_only_file)
            os.symlink(read_only_file, link_to_read_only_file)

        _create_read_only_file(read_only_file)

        # When
        with ZipFile(path) as zp:
            zp.extractall(self.tempdir)

        original_md5 = compute_md5(r_file)

        _create_link_to_ro(r_file)

        with ZipFile(path) as zp:
            zp.extractall(self.tempdir)
        files = list_files(self.tempdir)

        # Then
        self.assertCountEqual(files, r_files)
        self.assertTrue(os.path.islink(r_link))
        self.assertFalse(os.path.islink(r_file))
        self.assertEqual(compute_md5(r_file), original_md5)
        # Making sure we did not modify the file originally linked to
        # by the overwritten symlink
        self.assertEqual(
            compute_md5(read_only_file), hashlib.md5(some_data).hexdigest()
        )

    def test_add_tree(self):
        # Given
        path = os.path.join(self.tempdir, "foo.zip")

        source_dir = os.path.join(self.tempdir, "from")

        extract_dir = os.path.join(self.tempdir, "to")
        os.makedirs(extract_dir)

        files = [
            os.path.join(source_dir, "foo.txt"),
            os.path.join(source_dir, "foo", "fubar", "foo.txt"),
        ]
        r_files = [
            os.path.join(extract_dir, "foo.txt"),
            os.path.join(extract_dir, "foo", "fubar", "foo.txt"),
        ]

        for f in files:
            os.makedirs(os.path.dirname(f))
            with open(f, "wb") as fp:
                fp.write(b"yolo")

        # When
        with ZipFile(path, "w") as zp:
            zp.add_tree(source_dir)

        # Then
        with ZipFile(path) as zp:
            zp.extractall(extract_dir)
            self.assertCountEqual(
                zp.namelist(),
                ["foo/", "foo/fubar/", "foo.txt", "foo/fubar/foo.txt"]
            )

        for f in r_files:
            os.path.exists(f)
            with open(f, "rb") as fp:
                self.assertEqual(fp.read(), b"yolo")

        # Given
        r_files = [
            os.path.join(extract_dir, "from", "foo.txt"),
            os.path.join(extract_dir, "from", "foo", "fubar", "foo.txt"),
        ]

        # When
        with ZipFile(path, "w") as zp:
            zp.add_tree(source_dir, True)

        # Then
        with ZipFile(path) as zp:
            zp.extractall(extract_dir)
            self.assertCountEqual(
                zp.namelist(),
                ["from/foo/", "from/foo/fubar/", "from/foo.txt", "from/foo/fubar/foo.txt"]
            )

        for f in r_files:
            os.path.exists(f)
            with open(f, "rb") as fp:
                self.assertEqual(fp.read(), b"yolo")


class TestsPermissionExtraction(unittest.TestCase):
    def setUp(self):
        permissions = {
            'user': (stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR),
            'group': (stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP),
            'other': (stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH),
            'special': (stat.S_ISUID, stat.S_ISGID, stat.S_ISVTX)
        }
        self.files = []
        name_pattern = '{permgroup:s}_{octalcode:03b}_{specialcode:03b}'

        self.tempdir = tempfile.mkdtemp()
        self.filename = os.path.join(self.tempdir,
                                     "yoyo_{0}_tmp".format(os.getpid()))

        for permgroup in ('user', 'group', 'other'):
            for index in range(8):
                for specialindex in range(3):
                    filename = name_pattern.\
                        format(permgroup=permgroup, octalcode=index,
                               specialcode=specialindex)
                    path = os.path.join(self.tempdir, filename)
                    with open(path, 'wt') as file_:
                        file_.write(filename)
                    mode = stat.S_IRUSR
                    for order in range(3):
                        if index & 1 << order:
                            mode |= permissions[permgroup][order]
                    for order in range(3):
                        if specialindex & 1 << order:
                            mode |= permissions['special'][order]
                    os.chmod(path, mode)
                    real_permission = os.stat(path).st_mode & 0xFFF
                    self.files.append((path, real_permission))

        with ZipFile(self.filename, 'w', zipfile.ZIP_STORED) as zipfp:
            for path, mode in self.files:
                filename = os.path.basename(path)
                path = os.path.join(self.tempdir, filename)
                zipfp.write(path, filename)
                os.chmod(path, stat.S_IWRITE)
                os.remove(path)

    def tearDown(self):
        shutil.rmtree(self.tempdir, onerror=handle_readonly)

    def test_extractall_preserve_none(self):
        umask = os.umask(0)
        os.umask(umask)
        with ZipFile(self.filename, 'r') as zipfp:
            zipfp.extractall(self.tempdir)
            for path, mode in self.files:
                expected_mode = 0o666 & ~umask
                self.assertTrue(os.path.exists(path))
                self.assertEqual(os.stat(path).st_mode & 0xFFF,
                                 expected_mode)

    def test_extractall_preserve_safe(self):
        with ZipFile(self.filename, 'r') as zipfp:
            zipfp.extractall(self.tempdir,
                             preserve_permissions=PERMS_PRESERVE_SAFE)
            for filename, mode in self.files:
                expected_mode = mode & 0x1FF
                self.assertTrue(os.path.exists(filename))
                self.assertEqual(os.stat(filename).st_mode & 0xFFF,
                                 expected_mode)

    def test_extractall_preserve_all(self):
        with ZipFile(self.filename, 'r') as zipfp:
            zipfp.extractall(self.tempdir,
                             preserve_permissions=PERMS_PRESERVE_ALL)
            for filename, mode in self.files:
                self.assertTrue(os.path.exists(filename))
                self.assertEqual(os.stat(filename).st_mode & 0xFFF, mode)

    def test_extract_preserve_none(self):
        umask = os.umask(0)
        os.umask(umask)
        with ZipFile(self.filename, 'r') as zipfp:
            for filename, mode in self.files:
                arcname = os.path.basename(filename)
                zipfp.extract(arcname, path=self.tempdir)
                expected_mode = 0o666 & ~umask
                self.assertTrue(os.path.exists(filename))
                self.assertEqual(os.stat(filename).st_mode & 0xFFF,
                                 expected_mode)

    def test_extract_preserve_safe(self):
        with ZipFile(self.filename, 'r') as zipfp:
            for filename, mode in self.files:
                arcname = os.path.basename(filename)
                zipfp.extract(arcname, path=self.tempdir,
                              preserve_permissions=PERMS_PRESERVE_SAFE)
                expected_mode = mode & 0x1FF
                self.assertTrue(os.path.exists(filename))
                self.assertEqual(os.stat(filename).st_mode & 0xFFF,
                                 expected_mode)

    def test_extract_preserve_all(self):
        with ZipFile(self.filename, 'r') as zipfp:
            for filename, mode in self.files:
                arcname = os.path.basename(filename)
                zipfp.extract(arcname, path=self.tempdir,
                              preserve_permissions=PERMS_PRESERVE_ALL)
                self.assertTrue(os.path.exists(filename))
                self.assertEqual(os.stat(filename).st_mode & 0xFFF, mode)

    @unittest.skipIf(not SUPPORT_SYMLINK,
                     "this platform does not support symlink")
    def test_extract_preserve_safe_with_symlink(self):
        # Given
        python27 = os.path.join(self.tempdir, "bin", "python2.7")
        python = os.path.join(self.tempdir, "bin", "python")

        # When
        with ZipFile(ZIP_WITH_SOFTLINK_AND_PERMISSIONS) as zipfp:
            zipfp.extractall(self.tempdir,
                             preserve_permissions=PERMS_PRESERVE_SAFE)

        # Then
        self.assertTrue(os.path.exists(python))
        self.assertTrue(os.path.islink(python))
        self.assertTrue(os.path.exists(python27))
        self.assertTrue(os.access(python27, os.X_OK))
