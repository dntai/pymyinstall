"""
@file
@brief Install or update all packages.
"""
from __future__ import print_function
import os
import warnings
from ..installhelper import ModuleInstall, has_pip, update_pip
from ..installhelper.module_install_exceptions import MissingVersionOnPyPiException, MissingPackageOnPyPiException
from ..installhelper.module_dependencies import missing_dependencies
from .packaged_config_full_set import ensae_fullset


def _build_reverse_index():
    """
    builds a reverse index of the module,
    """
    res = {}
    mods = ensae_fullset()
    for m in mods:
        res[m.name] = m
        if m.mname is not None:
            res[m.mname] = m
    return res


_reverse_module_index = _build_reverse_index()


def find_module_install(name):
    """
    checks if there are specific instructions to run before installing module *name*,
    on Windows, some modules requires compilation, if not uses default option with *pip*

    @param      name        module name, the name can include a specific version number with '=='
    @return                 @see cl ModuleInstall
    """
    if '=' in name:
        spl = name.split('==')
        if len(spl) != 2:
            raise ValueError("unable to interpret " + name)
        name = spl[0]
        version = spl[1]
    else:
        version = None

    if name in _reverse_module_index:
        mod = _reverse_module_index[name]
    else:
        mod = ModuleInstall(name, "pip")

    if version is not None:
        mod.version = version
    return mod


def reorder_module_list(list_module):
    """
    reorder a list of modules to install, a module at position *p*
    should not depend not module at position *p+1*

    @param      list_module     list of module (@see cl ModuleInstall)
    @return                     list of modules

    The function uses modules stored in :mod:`pyminstall.packaged.packaged_config`,
    it does not go to pypi. If a module was not registered, it will be placed
    at the end in the order it was given to this function.
    """
    inset = {m.name: m for m in list_module}
    res = []
    for mod in ensae_fullset():
        if mod.name in inset:
            res.append(mod.copy(version=inset[mod.name].version))
            inset[mod.name] = None
    for mod in list_module:
        if inset[mod.name] is not None:
            res.append(mod)
    return res


def update_all(temp_folder=".", fLOG=print, verbose=True,
               list_module=None, reorder=True,
               skip_module=None):
    """
    update modules in *list_module*
    if None, this list will be returned by @see fn ensae_fullset,
    the function starts by updating pip.

    @param  temp_folder     temporary folder
    @param  verbose         more display
    @param  list_module     None or of list of str or @see cl ModuleInstall
    @param  fLOG            logging function
    @param  reorder         reorder the modules to update first modules with less dependencies (as much as as possible)
    @param  skip_module     module to skip (list of str)

    .. versionchanged:: 1.3
        Catch an exception while updating modules and walk through the end of the list.
        The function should be run a second time to make sure an exception remains.
        It can be due to python keeping in memory an updated module.
    """
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    if not has_pip():
        from .get_pip import main
        main()

    if skip_module is None:
        skip_module = []

    if list_module is None:
        from ..packaged import ensae_fullset
        list_module = ensae_fullset()
    else:
        list_module = [find_module_install(mod) if isinstance(
            mod, str) else mod for mod in list_module]

    list_module = [_ for _ in list_module if _.name not in skip_module]

    if reorder:
        list_module = reorder_module_list(list_module)

    if verbose:
        fLOG("update pip if needed")
    update_pip()
    modules = list_module
    again = []
    errors = []
    for mod in modules:
        if verbose:
            fLOG("check module: ", mod.name)

        is_installed = mod.is_installed()
        if not is_installed:
            continue

        try:
            has_update = mod.has_update()
        except (MissingVersionOnPyPiException, MissingPackageOnPyPiException) as e:
            # this happens for custom made version such as xgboost
            fLOG("    - unable to check updates", e)
            has_update = False
        if not has_update:
            continue

        ver = mod.get_pypi_version()
        inst = mod.get_installed_version()
        m = "    - updating module  {0} --- {1} --> {2} (kind={3})" \
            .format(mod.name, inst, ver, mod.kind)
        fLOG(m)
        try:
            b = mod.update(temp_folder=temp_folder, log=verbose)
        except Exception as e:
            b = False
            m = "    - failed to update module  {0} --- {1} --> {2} (kind={3}) due to {4}" \
                .format(mod.name, inst, ver, mod.kind, str(e))
            fLOG(m)
            errors.append((mod, e))
        if b:
            again.append(m)

    if verbose:
        fLOG("")
        fLOG("updated modules")
        for m in again:
            fLOG("  ", m)
        if len(errors) > 0:
            fLOG("failed modules")
            for m in errors:
                fLOG("  ", m)


def install_all(temp_folder=".", fLOG=print, verbose=True,
                list_module=None, reorder=True, skip_module=None,
                up_pip=True):
    """
    install modules in *list_module*
    if None, this list will be returned by @see fn ensae_fullset,
    the function starts by updating pip.

    @param  temp_folder     temporary folder
    @param  verbose         more display
    @param  list_module     None or of list of str or @see cl ModuleInstall
    @param  fLOG            logging function
    @param  reorder         reorder the modules to update first modules with less dependencies (as much as as possible)
    @param  skip_module     module to skip (list of str)
    @param  up_pip          upgrade pip
    """
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    if not has_pip():
        fLOG("install pip")
        from .get_pip import main
        main()

    if skip_module is None:
        skip_module = []

    if list_module is None:
        from ..packaged import ensae_fullset
        list_module = ensae_fullset()
    else:
        list_module = [find_module_install(mod) if isinstance(
            mod, str) else mod for mod in list_module]

    list_module = [_ for _ in list_module if _.name not in skip_module]

    if reorder:
        list_module = reorder_module_list(list_module)

    if up_pip:
        if verbose:
            fLOG("update pip if needed")
        update_pip()

    modules = list_module
    again = []
    errors = []
    for mod in modules:
        if verbose:
            fLOG("check module: ", mod.name)
        if not mod.is_installed():
            ver = mod.version
            m = "    - installing module  {0} --- --> {1} (kind={2})" \
                .format(mod.name, ver, mod.kind)
            fLOG(m)
            try:
                b = mod.install(temp_folder=temp_folder, log=verbose)
            except Exception as e:
                b = False
                m = "    - failed to update module  {0} --- {1} --> {2} (kind={3}) due to {4}" \
                    .format(mod.name, inst, ver, mod.kind, str(e))
                fLOG(m)
                errors.append((mod, e))
            if b:
                again.append(m)

    if verbose:
        fLOG("")
        fLOG("installed modules")
        for m in again:
            fLOG("  ", m)
        if len(errors) > 0:
            fLOG("failed modules")
            for m in errors:
                fLOG("  ", m)

    miss = missing_dependencies()
    if len(miss) > 0:
        mes = "\n".join("{0} misses {1}".format(k, ", ".join(v))
                        for k, v in sorted(miss.items()))
        warnings.warn(mes)
