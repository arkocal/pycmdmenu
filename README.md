# cmdmenu

`cmdmenu` is a simple library based on `argparse` for automatically creating command line interfaces
consisting of levels of hierarchy (like git) and linking them to functions.

## Installation

Run `pip install cmdmenu`

## Usage

See `/examples` for full exampes.

### Adding commands

Use the `cmdmenu.add_command` function for adding commands.

```python
import argparse
import cmdmenu

def echo(message):
    print(message)

def mirror_echo(message):
    print(message[::-1])

parser = argparse.ArgumentParser("An example application")
subparsers = parser.add_subparsers()

cmdmenu.add_command(subparsers, echo)
cmdmenu.parse_and_run_with(parser)
```

Run like this.
```
$ python main.py echo Hello
Hello
$ python main.py mirror_echo Hello
olleH
```

You can add a help message and a description to your commands using the
`cmdmenu_function` decorator. If you only specify one parameter, it will be used for both,
otherwise, the first one is the short help message, the second one is the description.

You can also add a string annotation to function parameters to generate help message

```python
@cmdmenu.cmdmenu_function("Echo to terminal", "Longer description of echo")
def echo(message: "Message to echo"):
    print(message)
```

```
$ python main.py --help
usage: An example application [-h] {echo,mirror_echo} ...

positional arguments:
  {echo,mirror_echo}
    echo              Echo to terminal
    mirror_echo       Echo reversed

optional arguments:
  -h, --help          show this help message and exit
$ python main.py echo --help
usage: An example application echo [-h] message

Longer description of echo

positional arguments:
  message     Message to echo

optional arguments:
  -h, --help  show this help message and exit
```

#### Default values
`cmdmenu` respects parameter default values. If a parameter has a default value, a flag will
be created for it. You can override the flag name using a dictionary annotation (see below) with the
`name` parameter.

```python
@cmdmenu.cmdmenu_function("Print a hello world message")
def hello(name=None):
    if name is None:
        print("Hello, World!")
    else:
        print("Hello, {}".format(name))
```

```
$ python main.py hello
Hello, World!
$ python main.py hello --name Ali
Hello, Ali!
```


#### More annotations
You can pass a dictionary as parameter annotation, the arguments are then passed to `argparse`.
See `add_command` docstring for more details.

```python
@cmdmenu.cmdmenu_function("Print sum of given numbers")
def add_numbers(numbers: {"help": "Numbers to sum up",
                  "nargs": "+", "type":int}):
    print(sum(numbers))
```

```
$ python main.py add_numbers 1 2 3
6
```

### Adding modules

You can all functions marked by the `cmdmenu_function` in a module (and its submodules)
using the `add_module` function.

You can save the functions from previous example in my_commands.py, and run the following

```python
import argparse
import cmdmenu

import my_commands

if __name__ == "__main__":
    parser = argparse.ArgumentParser("An example application")
    subparsers = parser.add_subparsers()

    cmdmenu.add_module(subparsers, my_commands, toplevel=True)
    cmdmenu.parse_and_run_with(parser)
```

This will create an identical program. The `toplevel=True` parameter indicates that the functions
should be added directly without creating an editional level.

By default `add_module` adds all the submodules of given module, which contain a variable called
`CMDMENU_META`.

Take the following structure as
an example:
```
main.py
fakegit
    __init__.py -> defines add, rm
    remote.py -> defines add rename
    my_addon/
	features -> defines foo, bar
	items -> defines baz
```

By adding fakegit as a toplevel, you get the following commands, each with positional and keyword
arguments as defined by the functions:
```
python main.py add
python main.py rm
python main.py remote add
python main.py remote rename
python main.py my_addon features foo
python main.py my_addon features bar
python main.py items baz
```

Submodule menu behaviour and documentation can be configured with a `CMDMENU_META` dictionary.
See `add_module` docstring for details.
