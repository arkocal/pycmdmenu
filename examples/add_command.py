import argparse
import cmdmenu

@cmdmenu.cmdmenu_module_func
def echo_configpath(configpath:"Path to config file"="config"):
    print("Config file path:", configpath)

@cmdmenu.cmdmenu_function("Echo to terminal", "Longer description of echo")
def echo(message: "Message to echo"):
    print(message)

@cmdmenu.cmdmenu_function("Echo reversed", "Longer description of mirror-echo")
def mirror_echo(message: "Message to echo reversed"):
    print(message[::-1])

@cmdmenu.cmdmenu_function("Print a hello world message")
def hello(name=None):
    if name is None:
        print("Hello, World!")
    else:
        print("Hello, {}!".format(name))

@cmdmenu.cmdmenu_function
def getkw(**kwargs):
    pass

@cmdmenu.cmdmenu_function("Print sum of given numbers")
def add_numbers(numbers: {"help": "Numbers to sum up",
                  "nargs": "+", "type":int}):
    print(sum(numbers))

if __name__=="__main__":
    parser = argparse.ArgumentParser("An example application")
    subparsers = parser.add_subparsers()

    cmdmenu.add_command(subparsers, echo)
    cmdmenu.add_command(subparsers, mirror_echo)
    cmdmenu.add_command(subparsers, add_numbers)
    cmdmenu.add_command(subparsers, hello)
    cmdmenu.parse_and_run_with(parser)
