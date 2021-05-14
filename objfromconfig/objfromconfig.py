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
    print("class is", clazz)
    tmpargs, tmpkwargs = build_args(inst.__init__, thedict)
    print(f"Calling init with {tmpargs}, {tmpkwargs}")
    inst.__init__(*tmpargs, **tmpkwargs)
    return inst


class ObjFromConfig:

    @classmethod
    def from_config(cls, config):
        return class_from_dict(config)

    def store_config(self, ldict):
        initfunc = self.__init__
        parms = list(signature(initfunc).parameters.items())
        cfg = {}
        # MAYBE: check if the value of the parm is its default value, if yes, do not store in config!
        for n, p in parms:
            # check if parm has a default value
            # if yes, check if that value is identical to the ldict value, if yes, do not store in config
            if p.default is not None and p.default == ldict[n]:
                print("Skipping", n)
                continue
            cfg[n] = ldict[n]
        cfg["$class"] = f"{self.__module__}.{type(self).__name__}"
        self._objfromconfig_cfg = cfg

    def get_config(self):
        return self._objfromconfig_cfg



