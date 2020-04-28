# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# builtin
import logging

# internal
from stixmarx.version import __version__  # noqa

formatter = logging.Formatter("[%(name)s] [%(levelname)-7s] [%(asctime)s] %(message)s")

# Console Handler for stixmarx messages
ch = logging.StreamHandler()
ch.setFormatter(formatter)

# Module-level logger
log = logging.getLogger(__name__)
log.addHandler(ch)
log.propagate = False


def parse(xml_input, encoding=None):
    from stixmarx import parser
    from stixmarx import container

    stix_package = parser.parse_xml(xml_input, encoding)
    marking_container = container.MarkingContainer(stix_package)

    return marking_container


def new():
    from stixmarx import container
    from stix.core import STIXPackage

    return container.MarkingContainer(STIXPackage())
