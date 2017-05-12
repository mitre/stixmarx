# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# builtin
import logging

# internal
from stixmarx import utils

# Module-level logger
LOG = logging.getLogger(__name__)

FIELDS = {}


def _initialize_fields():
    utils._load_stix()
    utils._load_cybox()
    utils._load_maec()
    utils._load_mixbox()

    if utils.stix:
        if utils.stix.__version__ == "1.1.1.8":
            from stixmarx.fields.stix.stix1118 import _FIELDS
            FIELDS.update(_FIELDS)
        elif utils.stix.__version__ == "1.2.0.1":
            from stixmarx.fields.stix.stix1201 import _FIELDS
            FIELDS.update(_FIELDS)
        elif utils.stix.__version__ == "1.2.0.2":
            from stixmarx.fields.stix.stix1202 import _FIELDS
            FIELDS.update(_FIELDS)
        elif utils.stix.__version__ == "1.2.0.3":
            from stixmarx.fields.stix.stix1203 import _FIELDS
            FIELDS.update(_FIELDS)
        elif utils.stix.__version__ == "1.2.0.4":
            from stixmarx.fields.stix.stix1203 import _FIELDS
            FIELDS.update(_FIELDS)
        else:
            message = "No compatible stix version found. Got {0}"
            LOG.warning(message.format(utils.stix.__version__))
    else:
        message = "No STIX library found in environment."
        LOG.debug(message)

    if utils.cybox:
        if utils.cybox.__version__ == "2.1.0.13":
            from stixmarx.fields.cybox.cybox21013 import _FIELDS
            FIELDS.update(_FIELDS)
        elif utils.cybox.__version__ == "2.1.0.14":
            from stixmarx.fields.cybox.cybox21013 import _FIELDS
            FIELDS.update(_FIELDS)
        else:
            message = "No compatible cybox version found. Got {0}"
            LOG.warning(message.format(utils.cybox.__version__))
    else:
        message = "No CybOX library found in environment."
        LOG.debug(message)

    if utils.maec:
        if utils.maec.__version__ == "4.1.0.13":
            from stixmarx.fields.maec.maec41013 import _FIELDS
            FIELDS.update(_FIELDS)
        else:
            message = "No compatible maec version found. Got {0}"
            LOG.warning(message.format(utils.maec.__version__))
    else:
        message = "No MAEC library found in environment."
        LOG.debug(message)

_initialize_fields()
