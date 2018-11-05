"""Automatically create command line menus with arg hiearchies."""
import argparse
import copy
import inspect
import pkgutil
from types import ModuleType

FUNC_NAME_ARG = "_cmdmenu_func_name"


def _merge_funcs(funcs):
    """Merge funcs into a single function.

    The resulting function will take all the parameters the given
    functions take, and execute the functions in given order.
    """
    # Function parameters should be given in a specific order
    # when constructing functions. Lower rang stand for a parameter
    # that comes first
    def param_rang(param):
        if param.kind == param.VAR_POSITIONAL:
            return 3
        if param.kind == param.VAR_KEYWORD:
            return 4
        if param.default == inspect._empty:
            return 1
        return 2

    def merged_func(*args, **kwargs):
        for func in funcs:
            sig = inspect.signature(func)
            if inspect.Parameter.VAR_KEYWORD not in [arg.kind for arg in sig.parameters.values()]:
                kwargs_func = {k:v for k,v in kwargs.items() if k in sig.parameters.keys()}
            func(*args, **kwargs_func)

    combined_par = {}
    for func in funcs:
        combined_par.update(inspect.signature(func).parameters)

    sig = inspect.signature(merged_func)
    sorted_params = sorted(combined_par.values(), key=param_rang)
    merged_func.__signature__ = sig.replace(parameters=sorted_params)
    merged_func.__name__ = funcs[-1].__name__
    return merged_func


def cmdmenu_function(param, description=None):
    """Decorator for marking a function to appear in cmdmenu.

    If it is used without a parameter, the function will only be
    marked (necassary for add_build).
    Otherwise it takes two single str, first one is help message,
    second one is description (optional).
    """
    def decorator(func):
        func.cmdmenu_help = param
        if description is not None:
            func.cmdmenu_description = description
        else:
            func.cmdmenu_description = param
        func.cmdmenu_is_marked = True
        return func
    # Decorator used with parameter (return actual decorator)
    if isinstance(param, str):
        return decorator
    # Decorator used without parameter (this is the actual decorator)
    if callable(param):
        param.cmdmenu_is_marked = True
        return param
    raise ValueError("Invalid parameters")

def cmdmenu_module_func(param):
    param.cmdmenu_is_marked_as_module_func = True
    return param

def add_command(subparsers, command_function):
    """Add a command function to argparse subparser.

    params:
    --------------------
    subparsers: The argparse._SubParsersAction object to add command to.
    command_function: A python function.

    Using the cmdmenu_function decorator, a menu description can be added
    to the command.

    Using parameter annotations menu options can be configured. For each
    parameter the annotation is either a string containing a help message
    of a dictionary containing parameters for the 'add_argument' method from
    argparse.ArgumentParser. 'dest' argument is not allowed.

    "name": name or flags (positional in add_argument), either a string
    or a list of strings. Defaults to parameter_name for parameters with no
    default value, and --parameter_name for others.
    "default": defaults to parameter default value, overrides if provided.

    All other parameters are passed directly.
    """
    subparser = subparsers.add_parser(command_function.__name__,
                                      help=getattr(command_function,
                                                   "cmdmenu_help", ""),
                                      description=getattr(command_function,
                                                          "cmdmenu_description",
                                                          ""))
    sig = inspect.signature(command_function)

    if FUNC_NAME_ARG in sig.parameters.keys():
        raise ValueError("Parameter name {} not allowed for cmdmenu "
                         "function {}.".format(FUNC_NAME_ARG,
                                               command_function.__name__))

    for param_name, param in sig.parameters.items():
        # do not add *args, **kwargs to menu
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            continue
        # Do not change the actual annotation
        meta = copy.deepcopy(param.annotation)
        if isinstance(meta, str):
            meta = {"help": meta}
        if not isinstance(meta, dict):
            meta = {}
        # dest is set automatically as it has to match parameter name
        if "dest" in meta:
            raise ValueError("'dest' not allowed in annotation dict of cmdmenu"
                             " function {}.".format(command_function.__name__))

        # Annotated default overrides python argument default
        if "default" not in meta.keys() and param.default is not inspect._empty:
            meta["default"] = param.default

        name_and_flags = meta.pop("name", None)
        if name_and_flags is None:
            if param.default is inspect._empty:
                name_and_flags = param_name
            # Assume parameter is optional if default value is provided
            else:
                name_and_flags = "--{}".format(param_name)
        if isinstance(name_and_flags, str):
            name_and_flags = [name_and_flags]
        # If optional parameter, make sure dist is the parameter name
        if name_and_flags[0].startswith("-"):
            meta["dest"] = param_name

        subparser.add_argument(*name_and_flags, **meta)
    subparser.set_defaults(**{FUNC_NAME_ARG:command_function})


def add_module(subparsers, module, parser=None, recursive=True, toplevel=None):
    """Add a command function to argparse subparser.

    It will add functions marked with the cmdmenu_function decorator,
    and (if recursive=True) submodules containing a CMDMENU_META var.

    params:
    --------------------
    subparsers: The argparse._SubParsersAction object to add command to.
    module: Module to be added. A CMDMENU_META variable of the module
    can be used to configure argparse.
    recursive (boolean): Whether to add submodules recursively.
    toplevel (boolean): If True, content of the module will be added
    directly to subparsers level, otherwise a new subparser will be created.
    Defaults to False, unless CMDMENU_META dictionary overrides it. Explicit
    value will override both.

    If you define CMDMENU_META for the module or any of the submodules,
    elements of this dictionary will be passed as parameters to
    subparsers.add_parser.
    "name" will be passed as a first positional argument, "toplevel" will
    not be passed but used as the toplevel parameter of the module when
    adding modules recursively.
    """
    # Do not change the original module variables.
    meta = copy.deepcopy(getattr(module, "CMDMENU_META", {}))

    if toplevel is None:
        toplevel = meta.pop("toplevel", False)

    if toplevel:
        add_to_subparsers = subparsers
        add_to_parser = parser
    else:
        name = meta.pop("name", module.__name__.split(".")[-1])
        add_to_parser = subparsers.add_parser(name, **meta)
        add_to_subparsers = add_to_parser.add_subparsers()

    module_functions = [v for n, v in inspect.getmembers(module)
                if getattr(v, "cmdmenu_is_marked_as_module_func",
                           False) is True]


    # Only add functions marked with the cmdmenu_function decorator
    commands = [(n, v) for n, v in inspect.getmembers(module)
                if getattr(v, "cmdmenu_is_marked", False) is True]
    for name, func in commands:
        add_command(add_to_subparsers, _merge_funcs(module_functions +
                                                    [func]))

    if recursive and hasattr(module, "__path__"):
        for _, name, ispkg in pkgutil.iter_modules(module.__path__):
            submodule = __import__(module.__name__+"."+name, fromlist=(name))
            if vars(submodule).get("IS_MENU_MODULE", False):
                add_module(add_to_subparsers, submodule, parser=add_to_parser,
                           recursive=ispkg)


def parse_and_run_with(argument_parser):
    """Run function with arguments from populated argument_parser."""
    args = vars(argument_parser.parse_args())
    func = args.pop(FUNC_NAME_ARG, None)
    if func is None:
        print(args)
    assert func is not None, "No function for given args"

    # If function does not take args or kwargs, just pass the fitting args.
    sig = inspect.signature(func)
    if inspect.Parameter.VAR_KEYWORD not in [arg.kind for arg in sig.parameters.values()]:
        args = {k:v for k,v in args.items() if k in sig.parameters.keys()}
    return func(**args)


def run(toplevel=None, module=None, *args, **kwargs):
    """Create a parser, parse args and run module.

    params:
    ----------
    toplevel: module or list of modules, added as toplevels (see add_module)
    module: module or list of modules, added with module-name arg (not toplevel)
    *args, **kwargs: Passed directly to ArgumentParser constructor
    """
    argument_parser = argparse.ArgumentParser(*args, **kwargs)
    subparsers = argument_parser.add_subparsers()

    if toplevel is None:
        toplevel = []
    elif isinstance(toplevel, ModuleType):
        toplevel = [toplevel]
    for m in toplevel:
        add_module(subparsers, m, parser=argument_parser, recursive=True,
                   toplevel=True)

    if module is None:
        module = []
    elif isinstance(module, ModuleType):
        module = [module]
    for m in module:
        add_module(subparsers, m, parser=argument_parser, recursive=True,
                   toplevel=False)

    parse_and_run_with(argument_parser)
