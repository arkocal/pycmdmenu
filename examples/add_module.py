import argparse
import cmdmenu

import add_command

if __name__ == "__main__":
    parser = argparse.ArgumentParser("An example application")
    subparsers = parser.add_subparsers()

    cmdmenu.add_module(subparsers, add_command, parser=parser, toplevel=True)
    cmdmenu.parse_and_run_with(parser)
