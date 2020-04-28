# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# stdlib
import logging
import argparse

from stixmarx import utils

# Module-level logger
LOG = logging.getLogger(__name__)


#  ----------------- MAIN SCRIPT  -----------------


def init_logging(level=logging.DEBUG):
    """Initialize Python logging.
        Args:
            level (int): Specifies the logging level."""
    fmt = "[%(asctime)s] [%(levelname)s] %(message)s"
    logging.basicConfig(level=level, format=fmt)


def _get_argparser():
    """Create and return an ArgumentParser for this application."""
    desc = "model-mapper v{0}".format(utils.ModelMapper.__version__)
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument(
        "--log-level",
        default="DEBUG",
        help="The logging output level.",
        choices=["DEBUG", "INFO", "WARN", "ERROR"]
    )

    parser.add_argument(
        "parse",
        default="",
        help="The name of the library to perform the mappings. (e.g. stix)"
    )

    return parser


def main(args):
    # Initialize logging
    init_logging(args.log_level)

    try:
        mapper = utils.ModelMapper(args.parse)
        mapper.to_file()
    except Exception as ex:
        LOG.exception(ex)


if __name__ == "__main__":
    # Parse the commandline args
    parser = _get_argparser()
    args = parser.parse_args()
    main(args)
