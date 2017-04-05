"""
@brief      test log(time=20s)

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


from src.pymyinstall.packaged import find_module_install
from pyquickhelper.loghelper import fLOG


class TestDownloadBottleChect(unittest.TestCase):

    def test_install_bottlechest(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        if sys.platform.startswith("win") and sys.version_info[0] == 2:
            # no pycrypto on Python 2.7 for Windows
            return

        fold = os.path.abspath(os.path.split(__file__)[0])
        temp = os.path.join(fold, "temp_download_bottlechest")
        if not os.path.exists(temp):
            os.mkdir(temp)
        for _ in os.listdir(temp):
            if os.path.isfile(os.path.join(temp, _)):
                os.remove(os.path.join(temp, _))

        if sys.platform.startswith("win"):
            fLOG("install", "bottlechest")
            m = find_module_install("Bottlechest")
            m.fLOG = fLOG
            exe = m.download(
                temp_folder=temp,
                file_save=os.path.join(
                    temp,
                    "out_page.html"), source="2")
            assert os.path.exists(exe)
            assert os.stat(exe).st_size > 100000
            if "cp{0}{1}-cp{0}{1}m-win_amd64".format(*sys.version_info[:2]) not in exe and \
               "cp{0}{1}-none-win_amd64".format(*sys.version_info[:2]) not in exe:
                raise Exception(exe)


if __name__ == "__main__":
    unittest.main()
