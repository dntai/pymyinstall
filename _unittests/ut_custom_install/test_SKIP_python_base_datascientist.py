"""
@brief      test log(time=12s)

skip this test for regular run
"""

import sys
import os
import unittest


try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

try:
    import pyquickhelper as skip_
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..",
                "..",
                "pyquickhelper",
                "src")))
    if path not in sys.path:
        sys.path.append(path)
    if "PYQUICKHELPER" in os.environ and len(os.environ["PYQUICKHELPER"]) > 0:
        sys.path.append(os.environ["PYQUICKHELPER"])
    import pyquickhelper as skip_


from src.pymyinstall.installcustom import install_python
from pyquickhelper.loghelper import fLOG, CustomLog
from pyquickhelper.pycode import get_temp_folder
from src.pymyinstall.packaged.packaged_config import datascientistbase_set


class TestDownloadPythonDataScienstist (unittest.TestCase):

    def test_install_python_data_scientist(self):
        """
        This test is using pymyinstall from pypi not the latest version
        of the sources.
        """
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        res = datascientistbase_set()
        self.assertTrue(res is not None)
        if not any(filter(lambda m: m.name == "toolz", res)):
            raise ImportError("toolz not found.")

        fold = os.path.abspath(os.path.split(__file__)[0])
        vers = "%d%d" % sys.version_info[:2]
        temp = os.path.join(fold, "temp_python%s" % vers)
        temp = get_temp_folder(
            __file__, "temp_pyds%s" % vers, max_path=True)
        down = get_temp_folder(
            __file__, "temp_pyds%s_download" % vers, clean=True, max_path=True)
        self.assertEqual(len(os.listdir(down)), 0)

        if sys.platform.startswith("win"):
            clog = CustomLog(temp)
            install_python(install=True, temp_folder=temp, fLOG=clog, custom=True,
                           download_folder=temp + "_download", modules="datascientistbase")
            pyt = os.path.join(temp, "python.exe")
            pip = os.path.join(temp, "Scripts", "pip.exe")
            if not os.path.exists(pyt):
                raise FileNotFoundError(pyt)
            if not os.path.exists(pip):
                raise FileNotFoundError(pip)


if __name__ == "__main__":
    unittest.main()
