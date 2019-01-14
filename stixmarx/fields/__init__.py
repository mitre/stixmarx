# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# builtin
import logging

# internal
from stixmarx import utils

# Module-level logger
LOG = logging.getLogger(__name__)

_FIELD_MAPPINGS = {}


def get_field_mappings():
    return _FIELD_MAPPINGS


def update_field_mappings(mappings):
    global _FIELD_MAPPINGS
    _FIELD_MAPPINGS.update(mappings)


def _initialize_fields():
    utils._load_stix()
    utils._load_cybox()
    utils._load_maec()
    utils._load_mixbox()

    if utils.stix:
        if utils.stix.__version__.startswith("1.1.1."):
            if utils.stix.__version__ in ("1.1.1.8", "1.1.1.9"):
                from stixmarx.fields.stix.stix1118 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
            else:
                from stixmarx.fields.stix.stix11110 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
                message = ("No compatible stix %s mappings found. Loaded "
                           "latest unchanged 1.1.1.10 field mappings.")
                LOG.info(message, utils.stix.__version__)

        elif utils.stix.__version__.startswith("1.2.0."):
            if utils.stix.__version__ == "1.2.0.1":
                from stixmarx.fields.stix.stix1201 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
            elif utils.stix.__version__ == "1.2.0.2":
                from stixmarx.fields.stix.stix1202 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
            elif utils.stix.__version__ == "1.2.0.3":
                from stixmarx.fields.stix.stix1203 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
            elif utils.stix.__version__ == "1.2.0.4":
                from stixmarx.fields.stix.stix1204 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
            elif utils.stix.__version__ == "1.2.0.5":
                from stixmarx.fields.stix.stix1205 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
            else:
                from stixmarx.fields.stix.stix1205 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
                message = ("No compatible stix %s mappings found. Loaded "
                           "latest unchanged 1.2.0.5 field mappings.")
                LOG.info(message, utils.stix.__version__)

        else:
            message = "No compatible stix version found. Got %s"
            LOG.warning(message, utils.stix.__version__)
    else:
        message = "No STIX library found in environment."
        LOG.debug(message)

    if utils.cybox:
        if utils.cybox.__version__.startswith("2.1.0."):
            if utils.cybox.__version__ in ("2.1.0.13", "2.1.0.14"):
                from stixmarx.fields.cybox.cybox21013 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
            elif utils.cybox.__version__ in ("2.1.0.15", "2.1.0.16"):
                from stixmarx.fields.cybox.cybox21016 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
            else:
                from stixmarx.fields.cybox.cybox21016 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
                message = ("No compatible cybox %s mappings found. Loaded "
                           "latest unchanged 2.1.0.16 field mappings.")
                LOG.info(message, utils.cybox.__version__)

        else:
            message = "No compatible cybox version found. Got %s"
            LOG.warning(message, utils.cybox.__version__)
    else:
        message = "No CybOX library found in environment."
        LOG.debug(message)

    if utils.maec:
        if utils.maec.__version__.startswith("4.1.0."):
            if utils.maec.__version__ == "4.1.0.13":
                from stixmarx.fields.maec.maec41013 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
            else:
                from stixmarx.fields.maec.maec41013 import _FIELDS
                _FIELD_MAPPINGS.update(_FIELDS)
                message = ("No compatible maec %s mappings found. Loaded "
                           "latest unchanged 4.1.0.13 field mappings.")
                LOG.info(message, utils.maec.__version__)
        else:
            message = "No compatible maec version found. Got %s"
            LOG.warning(message, utils.maec.__version__)
    else:
        message = "No MAEC library found in environment."
        LOG.debug(message)

_initialize_fields()
