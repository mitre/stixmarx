# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

"""
Defines a mapping of Python object properties to XML fieldnames.
"""

from stixmarx import fields
from stixmarx import utils


def is_attribute(fieldname):
    """Return True if the `fieldname` represents an XML attribute selector."""
    return fieldname.startswith("@")


def is_content(fieldname):
    """Return True if the `fieldname` represents an XML content selector."""
    return fieldname == "text()"


def is_element(fieldname):
    """Return True if the `fieldname` represents an XML element selector."""
    if is_attribute(fieldname):
        return False
    elif is_content(fieldname):
        return False
    else:
        return True


def xmlfield(entity, attr):
    """Return the XML field name for the mixbox Entity attribute.

    Args:
        entity: A mixbox Entity object.
        attr: An attribute name.

    Returns:
        An XML field selector for the associated Entity attribute. If no
        mapping exists, None is returned.
    """
    field_map = mapping(entity)
    return field_map.get(attr)


def mapping(entity):
    """Return a dictionary which maps the input `entity` attributes to
    XML field selectors.

    Args:
        entity: A mixbox Entity object.

    Returns:
        A dictionary which maps `entity` attributes to XML field selectors.
        If there is no mapping, an empty dictionary is returned.
    """
    klass = utils.fully_qualified_name(entity)
    nomap = {}

    if klass in fields.get_field_mappings():
        return fields.get_field_mappings().get(klass)
    else:
        return nomap
