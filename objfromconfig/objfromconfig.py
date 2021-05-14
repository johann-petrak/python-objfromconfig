"""
Module for creating objects from configuration dicts and retrieve the configuration dicts from objects.
"""


from inspect import signature
from inspect import Parameter
import importlib


def build_args(func, cfg):
    """
    Matches a configuration dictionary against the function parameters.
    """
    sig = signature(func)
    args = []
    kwargs = {}
    for cn in cfg.keys():
        if not cn.startswith("$") and cn not in sig.parameters:
            raise Exception(f"Function {func} does not have a parameter: {cn}")
    for n, p in sig.parameters.items():
        if n in cfg:
            val = cfg[n]
        else:
            # check if we have a default value for the parameter
            if p.default == Parameter.empty:
                raise Exception("No default and no value specified for parameter", n)
            else:
                # val = p.default
                continue
        if p.kind == Parameter.POSITIONAL_ONLY:
            args.append(val)
        elif p.kind == Parameter.POSITIONAL_OR_KEYWORD:
            args.append(val)
        elif p.kind == Parameter.VAR_POSITIONAL:
            # chekc if val is iterable?
            args.extend(val)
        elif p.kind == Parameter.KEYWORD_ONLY:
            kwargs[n] = val
        elif p.kind == Parameter.VAR_KEYWORD:
            # check if val is dict?
            kwargs.update(val)
    return args, kwargs


def class_from_dict(thedict):
    cpath = thedict["$class"]
    # cpath must be of the form [a.b.c.]ClassName
    # so we split on the last dot, if any
    pack, _, clname = cpath.rpartition(".")
    modul = importlib.import_module(pack)
    clazz = getattr(modul, clname)
    inst = clazz.__new__(clazz)
    tmpargs, tmpkwargs = build_args(inst.__init__, thedict)
    # recursively construct any nested objects, if necessary

    def replace_by_obj(val):
        if isinstance(val, dict) and "$class" in val:
            return class_from_dict(val)
        return val
    tmpargs = [replace_by_obj(arg) for arg in tmpargs]
    tmpkwargs = {n: replace_by_obj(arg) for n, arg in tmpkwargs.items()}
    inst.__init__(*tmpargs, **tmpkwargs)
    return inst


class ObjFromConfig:

    def __init__(self):
        self._objfromconfig_cfg = {}

    @classmethod
    def from_config(cls, config):
        return class_from_dict(config)

    def store_config(self, ldict):
        initfunc = self.__init__
        parms = list(signature(initfunc).parameters.items())
        cfg = {}
        for n, p in parms:
            # check if parm has a default value
            # if yes, check if that value is identical to the ldict value, if yes, do not store in config
            if p.default is not None and p.default == ldict[n]:
                continue
            # if an object has been created by a config, store the config instead of the object
            val = ldict[n]
            if isinstance(val, ObjFromConfig):
                val = val.get_config()
            cfg[n] = val
        cfg["$class"] = f"{self.__module__}.{type(self).__name__}"
        self._objfromconfig_cfg = cfg

    def get_config(self):
        return self._objfromconfig_cfg
