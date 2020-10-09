import os.path


HERE = os.path.dirname(__file__)

NOSE_EGG = os.path.join(HERE, "data", "nose.egg")
VTK_EGG = os.path.join(HERE, "data", "vtk.egg")
ZIP_WITH_SOFTLINK = os.path.join(HERE, "data", "zip_with_softlink.zip")
ZIP_WITH_DIRECTORY_SOFTLINK = os.path.join(HERE, "data", "zip_with_directory_softlink.zip")
ZIP_WITH_PERMISSIONS = os.path.join(HERE, "data", "zip_with_permissions.zip")
ZIP_WITH_SOFTLINK_AND_PERMISSIONS = os.path.join(
    HERE, "data", "zip_with_softlink_and_permissions.zip"
)

NOSE_SPEC_DEPEND = """\
metadata_version = '1.1'
name = 'nose'
version = '1.3.0'
build = 2

arch = 'amd64'
platform = 'darwin'
osdist = None
python = '2.7'
packages = []
"""
