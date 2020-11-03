""" Cli module. """

__version__ = "0.1"
__author__ = "Bernhard Esperester"

# system
from argparse import ArgumentParser

# pylib
from pylib.utilities.util_chitchat import \
    Chitchat, \
    ChitchatOption
from pylib.utilities.util_logbook import logbook
from pylib.utilities.util_validator import \
    Validator, \
    ValidationFailedException

# folderly
import app

from folderly import filesystem
from folderly import localize
from folderly import constants


def add_main_parsers(parser):
    pack_parser = parser.add_parser("pack", help="Pack folderly template.")
    
    #pack_parser.add_argument("-d", "--dry", dest="dry", action="store_true", help="Do a dry run.")
    pack_parser.add_argument("source", help="Source path.")
    pack_parser.add_argument("name", help="Template name.")
    pack_parser.add_argument("-e", "--exclude", dest="exclude", nargs="?", help="Exclude files via pattern (e.g. *.DS_Store,*.txt).")

    unpack_parser = parser.add_parser("unpack", help="Unpack folderly template.")
    unpack_parser.add_argument("destination", help="Destination path.")
    unpack_parser.add_argument("name", help="Template name.")

def add_config_subparsers(parser):
    """Add config subparsers.

    Args:
        parser
    """

    config_parser = parser.add_parser("config", help="Configure folderly.")

    config_subparsers = config_parser.add_subparsers(help="Config commands.", dest="config")

    # add install parser
    config_subparsers.add_parser("install", help="Install folderly template. Target specific version like this: <template>@<version>")

def handle_main_module(args, folderly):
    if args.module == "pack":
        # folderly.pack(args.source, args.name, args.exclude)

        # 1. collect directories and files from source directory
        paths_list = filesystem.gather(args.source)

        # 2. filter directories and files

               

        # 3. present result and continue / cancel

        chitchat_options = [
            ChitchatOption(Chitchat.CHOICE_YES, default=True),
            ChitchatOption(Chitchat.CHOICE_NO)
        ]

        filtered_paths_list_chitchat = Chitchat("Does this look alright?", chitchat_options)

        while not filtered_paths_list_chitchat.is_happy:
            logbook.clear()

            logbook.warning(args.exclude, "Exclude:")

            filtered_paths_list = filesystem.filter(paths_list, args.exclude)

            logbook.info(localize.TEXT_FOLLOWING_PATHS_WILL_BE_ADDED, "Please Note:")

            for path in sorted(filtered_paths_list):
                logbook.info(path, "+")

            filtered_paths_list_chitchat.ask()


        filtered_paths_list_is_good = False

        while not filtered_paths_list_is_good:
            logbook.clear()

            logbook.warning(args.exclude, "Exclude:")

            filtered_paths_list = filesystem.filter(paths_list, args.exclude)

            logbook.info(localize.TEXT_FOLLOWING_PATHS_WILL_BE_ADDED, "Please Note:")

            for path in sorted(filtered_paths_list):
                logbook.info(path, "+")

            selection = raw_input("Does this look alright? [Y,n]")

            if selection.lower() == "y":
                filtered_paths_list_is_good = True

        quit()

        # 4. gather data about template name, version, author and description

        package_data = constants.TEMPLATE_PACKAGE_DEFAULT.copy()

        validator = Validator(constants.TEMPLATE_PACKAGE_RULES, package_data)

        if not validator.is_valid:
            logbook.info("let me ask you for some information :-)", "Before we start,")

        while not validator.is_valid:
            def request_input(key, rules, value):
                """ Request user input to validate.

                Args:
                    key (str): Data key
                    rules (list): Validation rules
                    value (str): Current value
                Returns:
                    str
                """

                # request user input
                request_data = {
                    "key": key.title(),
                    "value": value
                }

                return raw_input("{key} [{value}]: ".format(**request_data)) or value

            try:
                validator.validate(request_input)
            except ValidationFailedException:
                logbook.error("The following validation errors occured:")

                for message in validator.messages:
                    logbook.error(message.message, message.name.title())

        print package_data

        # 5. pack directories and files into temp directory, zip folder and move to templates

    if args.module == "unpack":
        folderly.unpack(args.destination, args.name)

def cli():
    
    parser = ArgumentParser(description="Commandline interface for creating directory structures.", prog="folderly")

    subparsers = parser.add_subparsers(help="Submodules", dest="module")

    add_main_parsers(subparsers)

    add_config_subparsers(subparsers)

    folderly = app.init()

    args = parser.parse_args()

    handle_main_module(args, folderly)

    # try:
    #     # parse arguments
    #     args = parser.parse_args()

    #     handle_main_module(args, folderly)

    #     # handle_config_module(args, core)
    # except Exception as e:
    #     raise e