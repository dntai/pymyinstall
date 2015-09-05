"""
@file
@brief Creates batch file to set up the environment
"""
from __future__ import print_function

import os
import sys

if sys.version_info[0] == 2:
    from codecs import open


def create_win_batches(folders, verbose=False, selection=None, fLOG=print, module_list=None):
    """
    create batchs for the setup, they will be placed in
    *folders["config"]*

    @param      folders     dictionary with the keys *tools*, *config*, *python*, *workspace*
    @param      verbose     verbose
    @param      fLOG        logging function
    @param      selection   list of batchs to create
    @param      module_list list of python modules to install, to know which script to install or not
    @return                 operations (list of what was done)

    .. versionchanged:: 1.3
        Add batch file for glue and to run some checkings.
    """
    if selection is None:
        raise ValueError("selection cannot be None")
    if module_list is None:
        raise ValueError("module_list cannot be None")

    has_jupyter = False
    has_rodeo = False
    has_spyder = False
    has_rss = False
    has_glue = False
    for mod in module_list:
        if mod.name == "jupyter":
            has_jupyter = True
        if mod.name == "rodeo":
            has_rodeo = True
        if mod.name == "spyder":
            has_spyder = True
        if mod.name == "pyrsslocal":
            has_rss = True
        if mod.name == "glueviz":
            has_glue = True

    list_functions = [create_win_env,
                      create_win_scite,
                      create_win_putty,
                      create_win_sqllitespy,
                      create_win_python_console,
                      update_all_packages,
                      run_checkings,
                      win_replace_shebang,
                      ]

    if has_jupyter:
        list_functions.extend([create_win_jupyter_console,
                               create_win_jupyter_qtconsole,
                               create_win_jupyter_notebook,
                               win_install_kernels,
                               ])

    if has_rodeo:
        list_functions.append(create_win_rodeo)

    if has_spyder:
        list_functions.append(create_win_spyder)

    if has_rss:
        list_functions.append(create_win_rss)

    if has_glue:
        list_functions.append(create_win_glue)

    if "r" in selection:
        list_functions.append((create_win_r_console, "r"))
        list_functions.append((create_win_r_gui, "r"))

    if "julia" in selection:
        list_functions.append((create_win_julia_console, "julia"))

    operations = []
    for func in list_functions:
        if isinstance(func, tuple):
            func, name = func
        else:
            name = None

        if name is None or name in selection:
            op = func(folders)
            if verbose:
                for o in op:
                    fLOG(" ".join(o))
            operations.extend(op)
    return operations


def create_win_env(folders):
    """
    create a batch file to set up the environment

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    tools = folders["tools"]
    text = ["@echo off", "set CURRENT=%~dp0",
            "set PYTHON_TOOLS=%CURRENT%\\..\\tools",
            "set PYTHON_WINHOME=%CURRENT%\\..\\python",
            "set PYTHON_WINSCRIPTS=%CURRENT%\\..\\python\\Scripts",
            "set WORKSPACE=%CURRENT%\\..\\workspace",
            "set PATH=%PYTHON_WINHOME%;%PYTHON_WINSCRIPTS%;%PATH%"]
    if os.path.exists(os.path.join(tools, "R")):
        text.append("set R_HOME=%PYTHON_TOOLS%\\R")
        text.append("set R_LIBS=%PYTHON_TOOLS%\\R\\library")
    if os.path.exists(os.path.join(tools, "Julia")):
        text.append("set JULIA_HOME=%PYTHON_TOOLS%\\Julia")
        text.append("set JULIA_PKGDIR=%PYTHON_TOOLS%\\Julia\\pkg")
    if os.path.exists(os.path.join(tools, "MinGW")):
        text.append("set PATH=%PATH%;%PYTHON_TOOLS%\\MinGW\\bin")

    text = "\n".join(text)
    name = os.path.join(folders["config"], "env.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_jupyter_console(folders):
    """
    create a batch file to start jupyter

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off",
            "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set JUPYTERC=%PYTHON_WINSCRIPTS%\\jupyter-console.exe",
            "set IPYTHONRC=%PYTHON_WINSCRIPTS%\\ipython.exe",
            "%IPYTHONRC% console"]
    # command jupyter console does not work yet even if the documentation says
    # so

    text = "\n".join(text)
    name = os.path.join(folders["config"], "jupyter_console.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_jupyter_qtconsole(folders):
    """
    create a batch file to start Jupyter QtConsole

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set JUPYTERQTC=%PYTHON_WINSCRIPTS%\\jupyter-qtconsole.exe",
            "start %JUPYTERQTC%"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "jupyter_qtconsole.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_jupyter_notebook(folders):
    """
    create a batch file to start Jupyter Notebook

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set JUPYTERNB=%PYTHON_WINSCRIPTS%\\jupyter-notebook.exe",
            "%JUPYTERNB% --notebook-dir=%WORKSPACE% --config=%CURRENT2%\\profile_win_profile\\ipython_kernel_config.py"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "jupyter_notebook.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_rodeo(folders):
    """
    create a batch file to start rodeo

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set RODEO=%PYTHON_WINSCRIPTS%\\rodeo.exe",
            "%RODEO% %WORKSPACE%"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "rodeo.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_scite(folders):
    """
    create a batch file to start scite

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set SCITE=%PYTHON_TOOLS%\\Scite\\wscite\\scite.exe",
            "start %SCITE% %1"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "scite.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_putty(folders):
    """
    create a batch file to start scite

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set PUTTY=%PYTHON_TOOLS%\\Putty\\putty.exe",
            "start %PUTTY%"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "putty.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_sqllitespy(folders):
    """
    create a batch file to start sqlitespy

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set SQLITESPY=%PYTHON_TOOLS%\\SQLiteSpy\\SQLiteSpy.exe",
            "cd %WORKSPACE%",
            "start %SQLITESPY%"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "sqlitespy.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_python_console(folders):
    """
    create a batch file to start python

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set PYTHON=%PYTHON_WINHOME%\\python.exe",
            "%PYTHON%"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "python_console.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_julia_console(folders):
    """
    create a batch file to start julia

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "rem call %CURRENT2%\\env.bat",
            "set JULIA=%PYTHON_TOOLS%\\Julia\\bin\\julia.exe",
            "%JULIA%"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "julia_console.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_spyder(folders):
    """
    create a batch file to start spyder

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)

    .. index:: Spyder, PySide, PyQt

    This installation uses `PySide <https://pypi.python.org/pypi/PySide/1.2.2>`_
    instead of `PyQt <https://www.riverbankcomputing.com/software/pyqt/intro>`_.
    The environment variable ``QT_API`` needs to be set to ``pyside`` before
    running Spyder.

        set QT_API=pyside
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set QT_API=pyside",
            "%PYTHON_WINSCRIPTS%\\spyder.exe --workdir=%WORKSPACE%"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "spyder.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_r_console(folders):
    """
    create a batch file to start R

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set REXE=%PYTHON_TOOLS%\\R\\bin\\x64\\R.exe",
            "%REXE%"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "r_console.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_r_gui(folders):
    """
    create a batch file to start R Gui

    @param      folders     see @see fn create_win_batches
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            "set RGUI=%PYTHON_TOOLS%\\R\\bin\\x64\\Rgui.exe",
            "start %RGUI%"]

    text = "\n".join(text)
    name = os.path.join(folders["config"], "r_gui.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def win_install_kernels(folders, suffix=""):
    """
    create a batch file to install kernels

    @param      folders     see @see fn create_win_batches
    @param      suffix      add a suffix
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            '%PYTHON_WINHOME%\\python -u -c "from pymyinstall.win_installer import inno_install_kernels;inno_install_kernels(\'CURRENT2\', \'%1\')"']

    text = "\n".join(text)
    name = os.path.join(folders["config"], "add_kernels.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def win_replace_shebang(folders, suffix=""):
    """
    create a batch file to replace the shebang

    @param      folders     see @see fn create_win_batches
    @param      suffix      add a suffix
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            'if "%1"=="" (',
            '    set P1=EMPTY_STRING',
            ') ELSE (',
            '    set P1=%1',
            ')',
            'if "%2"=="" (',
            '    set P2=%PYTHON_WINHOME%',
            ') ELSE (',
            '    set P2=%2',
            ')',
            '%PYTHON_WINHOME%\\python -u -c "import os;from pymyinstall.win_installer import win_patch_paths;win_patch_paths(\'PYTHON_WINSCRIPTS\', [\'\', \'P1\'], \'P2\')"']

    text = "\n".join(text)
    name = os.path.join(folders["config"], "replace_shebang.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def create_win_rss(folders, suffix=""):
    """
    create a batch file to start RSS reader

    @param      folders     see @see fn create_win_batches
    @param      suffix      add a suffix
    @return                 operations (list of what was done)
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            '%PYTHON_WINHOME%\\python -u -c "from pyquickhelper import fLOG;from pyquickhelper.pycode.blog_helper import rss_update_run_server;fLOG(OutputPrint=True);rss_update_run_server(r\'%CURRENT2%rss_database.db3\', r\'%CURRENT2%rss_list.xml\')"']

    text = "\n".join(text)
    name = os.path.join(folders["config"], "run_fetch_rss.bat")
    with open(name, "w") as f:
        f.write(text)

    text = """
                <?xml version="1.0" encoding="UTF-8"?>
                <opml version="1.0">
                    <head>
                        <title>teachings subscriptions</title>
                    </head>
                    <body>
                        <outline text="XD blog" title="XD blog" type="rss"
                            xmlUrl="http://www.xavierdupre.fr/blog/xdbrss.xml"
                            htmlUrl="http://www.xavierdupre.fr/blog/xd_blog.html" />
                    </body>
                </opml>
                """.replace("                ", "")

    rss_name = os.path.join(folders["config"], "rss_list.xml")
    with open(rss_name, "w", encoding="utf8") as f:
        f.write(text)

    return [("batch", name), ("rss", rss_name)]


def create_win_glue(folders, suffix=""):
    """
    create a batch file to start Glue

    @param      folders     see @see fn create_win_batches
    @param      suffix      add a suffix
    @return                 operations (list of what was done)

    .. versionadded:: 1.3
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            '%PYTHON_WINSCRIPTS%\\glue.exe %1']

    text = "\n".join(text)
    name = os.path.join(folders["config"], "run_glue.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def update_all_packages(folders, suffix=""):
    """
    create a batch file to update all packages

    @param      folders     see @see fn create_win_batches
    @param      suffix      add a suffix
    @return                 operations (list of what was done)

    .. versionchanged:: 1.3
         Bug fix, update script to import function update_all (fails in 1.2).
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            '%PYTHON_WINHOME%\\python -u -c "from pymyinstall.packaged import update_all;update_all(temp_folder=\'%WORKSPACE%/update_modules\', verbose=True)"']

    text = "\n".join(text)
    name = os.path.join(folders["config"], "run_update_all_packages.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]


def run_checkings(folders, suffix=""):
    """
    create a batch file to update all packages

    @param      folders     see @see fn create_win_batches
    @param      suffix      add a suffix
    @return                 operations (list of what was done)

    .. versionadded:: 1.3
    """
    text = ["@echo off", "set CURRENT2=%~dp0",
            "call %CURRENT2%\\env.bat",
            '%PYTHON_WINHOME%\\python -u -c "from pymyinstall.win_installer import distribution_checkings;distribution_checkings(None, None)"']

    text = "\n".join(text)
    name = os.path.join(folders["config"], "run_checkings.bat")
    with open(name, "w") as f:
        f.write(text)
    return [("batch", name)]
