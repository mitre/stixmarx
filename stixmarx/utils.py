# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# builtins
import contextlib
import logging

# external
from mixbox.vendor.six import string_types

# internal
from stixmarx import errors
from stixmarx import xml

# Module-level logger
LOG = logging.getLogger(__name__)

# Lazy python-stix imports
stix = None
stix_core = None
stix_campaign = None
stix_common = None
stix_coa = None
stix_dm = None
stix_et = None
stix_incident = None
stix_indicator = None
stix_report = None
stix_ta = None
stix_ttp = None
stix_utils = None
stix_parser = None
stix_nsparser = None

# Lazy python-cybox imports
cybox = None
cybox_core = None
cybox_common = None
cybox_nsparser = None

# Lazy mixbox imports
mixbox = None
mixbox_entities = None

# Lazy python-maec imports
maec = None
maec_nsparser = None

# Flags for lazy imports
__PYTHON_STIX_LOADED = False
__PYTHON_CYBOX_LOADED = False
__PYTHON_MAEC_LOADED = False
__MIXBOX_LOADED = False


def _load_stix():
    global __PYTHON_STIX_LOADED
    global stix, stix_core, stix_campaign, stix_coa, stix_dm, stix_et
    global stix_incident, stix_indicator, stix_report, stix_ta, stix_ttp
    global stix_utils, stix_parser, stix_nsparser, stix_common

    if __PYTHON_STIX_LOADED:
        return

    try:
        import stix
        import stix.core as stix_core
        import stix.campaign as stix_campaign
        import stix.common as stix_common
        import stix.coa as stix_coa
        import stix.data_marking as stix_dm
        import stix.exploit_target as stix_et
        import stix.incident as stix_incident
        import stix.indicator as stix_indicator
        import stix.report as stix_report
        import stix.threat_actor as stix_ta
        import stix.ttp as stix_ttp
        import stix.utils as stix_utils
        import stix.utils.parser as stix_parser
        import stix.utils.nsparser as stix_nsparser
    except (ImportError, ImportWarning) as e:
        LOG.warning(e)
        return

    __PYTHON_STIX_LOADED = True


def _load_cybox():
    global __PYTHON_CYBOX_LOADED
    global cybox, cybox_core, cybox_common, cybox_nsparser

    if __PYTHON_CYBOX_LOADED:
        return

    try:
        import cybox
        import cybox.core as cybox_core
        import cybox.common as cybox_common
        import cybox.utils.nsparser as cybox_nsparser
    except (ImportError, ImportWarning) as e:
        LOG.warning(e)
        return

    __PYTHON_CYBOX_LOADED = True


def _load_mixbox():
    global __MIXBOX_LOADED
    global mixbox, mixbox_entities, mixbox_ns

    if __MIXBOX_LOADED:
        return

    try:
        import mixbox
        import mixbox.entities as mixbox_entities
        import mixbox.namespaces as mixbox_ns
    except (ImportError, ImportWarning) as e:
        LOG.warning(e)
        return

    __MIXBOX_LOADED = True


def _load_maec():
    global __PYTHON_MAEC_LOADED
    global maec, maec_nsparser

    if __PYTHON_MAEC_LOADED:
        return

    try:
        import maec
        import maec.utils.nsparser as maec_nsparser
    except (ImportError, ImportWarning) as e:
        LOG.warning(e)
        return

    __PYTHON_MAEC_LOADED = True


@contextlib.contextmanager
def ignored(*exceptions):
    """Allows you to ignore exceptions cleanly using context managers. This
    exists in Python 3.

    """
    try:
        yield
    except exceptions:
        pass


def fully_qualified_name(object_):
    return get_module(object_) + "." + class_name(object_)


def get_module(object_):
    return object_.__module__


def module_name(module_):
    return str(module_.__name__)


def class_name(object_):
    return object_.__class__.__name__


def contains_handling(entity):
    return hasattr(entity, "handling")


def is_stix_core(entity):
    _load_stix()
    return isinstance(entity, stix.BaseCoreComponent)


def is_stix_report(entity):
    _load_stix()
    if not stix_report:  # For python-stix < 1.2.0.0, there is no Report object
        return False
    return isinstance(entity, stix_report.Report)


def is_cybox_property(entity):
    _load_cybox()
    return isinstance(entity, cybox_common.ObjectProperties)


def is_marking_specification(marking):
    _load_stix()
    return isinstance(marking, stix_dm.MarkingSpecification)


def is_marking_structure(marking):
    _load_stix()
    return isinstance(marking, stix_dm.MarkingStructure)


def check_marking(marking):
    if is_marking_specification(marking):
        return

    msg = ("Attempting to mark object with incorrect type: '{0}'. Must be an "
           "instance of MarkingSpecification")
    msg = msg.format(type(marking))
    raise errors.UnknownMarkingError(message=msg, marking=marking)


def check_marking_struct(struct):
    if is_marking_structure(struct):
        return

    msg = "Expected '{0}' but received '{1}'"
    msg.format(stix_dm.MarkingStructure, type(struct))

    raise errors.UnknownMarkingError(message=msg, marking=struct)


def check_empty_marking(marking):
    if not marking.controlled_structure:
        return

    error = "Marking path must be empty. Found '{0}'"
    error = error.format(marking.controlled_structure)

    raise errors.MarkingPathNotEmpty(
        message=error,
        marking=marking
    )


def parse_package(xml_input, encoding=None):
    _load_stix()
    parser = stix_parser.EntityParser()
    return parser.parse_xml(xml_input, encoding=encoding)


def lookup(package, id_):
    entity = package.find(id_)

    if not entity:
        msg = "Failed to find entity in STIX Package with ID {0}"
        msg = msg.format(id_)
        raise errors.IdLookupError(message=msg, id_=id_)

    return entity


def get_handling(entity):
    _load_stix()

    try:
        header = entity.stix_header
        if not header:
            header = stix_core.STIXHeader()
            entity.stix_header = header
        base = header
    except AttributeError:
        # Entity was not a STIXPackage instance.
        base = entity

    if hasattr(base, "handling") and not base.handling:
        base.handling = stix_dm.Marking()

    # Handles stix.Report Handling case.
    elif hasattr(base, "header"):
        if not base.header:
            base.header = stix_report.header.Header()

        if not base.header.handling:
            base.header.handling = stix_dm.Marking()

        return base.header.handling

    return base.handling


def is_package(item):
    _load_stix()
    return isinstance(item, stix_core.STIXPackage)


def is_reference(item):
    try:
        return bool(item.idref)
    except AttributeError:
        return False


def contains_struct(spec, struct):
    structs = spec.marking_structures

    if not structs:
        return False

    if struct in structs:
        return True

    # Try to see if an equivalent struct is in the marking_spec
    struct_dict = struct.to_dict()
    return any(struct_dict == s.to_dict() for s in structs.to_list())


def contains_spec(specs, spec):
    def strip_cs(d):
        """Remove the 'controlled_structure' entry from the dictionary
        if it is present.

        """
        d.pop('controlled_structure', None)
        return d

    if not specs:
        return False

    if spec in specs:
        return True

    spec_dict = strip_cs(spec.to_dict())
    return any(spec_dict == strip_cs(s.to_dict()) for s in specs)


def fields(entity):

    if hasattr(entity, "typed_fields"):
        return entity.typed_fields
    elif hasattr(entity, "_get_vars"):
        return entity._get_vars()
    else:
        return []


def replace_xml_element(old, new):
    """Replaces `old` node with `new` in the document which `old` exists."""
    if old is new:
        return old

    parent = old.getparent()

    if parent is None:
        raise ValueError("Old value has no parent.")

    idx = parent.index(old)
    parent.insert(idx, new)
    parent.remove(old)


def is_entitylist(entity):
    _load_mixbox()
    return isinstance(entity, mixbox_entities.EntityList)


def is_skippable(owner, varname, varobj):

    if varname == "__datamarkings__" and isinstance(varobj, set):
        return True

    if varname == "__datamarkings__" and isinstance(owner, set):
        return True

    if varname == "_fields" and isinstance(varobj, dict):
        return True

    if varname == "_parent" and is_cybox_property(owner):
        return True

    if varname in ("__input_namespaces__", "__input_schemalocations__",
                   "__binding__"):
        return True

    return False


def is_entity(entity):
    _load_mixbox()
    return isinstance(entity, mixbox_entities.Entity)


def is_list(entity):
    return isinstance(entity, list)


def is_node(field):
    """Return True if `field` represents an XML Axis ``self::node()`` or
    ``descendant-or-self::node()`` selector, otherwise False.
    """
    return (xml.XPATH_AXIS_SELF_NODE in field or
            xml.XPATH_AXIS_DESCENDANT_OR_SELF_NODE in field)


def is_sequence(item):
    """Returns ``True`` if `value` is a sequence type (e.g., ``list``, or
    ``tuple``). String types will return ``False``.

    """
    return hasattr(item, "__iter__") and not isinstance(item, string_types)


def attr_name(path, name):
    """Converts `name` TypeField into the attribute name expected by
    MarkingSerializer when walking the object model.

    It will access the last entity instance through `path`, inspect its
    properties and match it against `name` TypeField.

    Arguments:
        name: A TypeField instance.
        path: A `list` that represents a given step while walking the
        python object model.

    """
    for x in path[-1].typed_fields_with_attrnames():
        val, tf = x

        if tf is name:
            return val


def load_nsmap():
    """It combines namespaces to prefix dictionaries of STIX, CybOX, MAEC and
    any other extension that registered their namespace with mixbox.

    Returns:
        Default Namespace to prefix aliases mapping.
    """
    _load_mixbox()

    return mixbox_ns.__ALL_NAMESPACES


def get_all_marking_specs(package):
    """
    This method will walk a STIX Package and return all the MarkingSpecification
    objects found in the input document. The method will only return markings
    that are explicitly set in the input document.

    Args:
        package: stix.core.STIXPackage object.

    Returns:
        list: Containing MarkingSpecification objects.
    """
    from . import navigator

    _load_stix()
    marking_specs = []

    for entity in navigator.iterwalk(package):
        if isinstance(entity, stix_dm.MarkingSpecification):
            marking_specs.append(entity)

    return marking_specs


def get_null_markings(package):
    """
    This method will walk a STIX Package and return all the MarkingSpecification
    objects found in the input document that do NOT contain a Controlled
    Structure. The method will only return markings that are explicitly set in
    the input document.

    Args:
        package: stix.core.STIXPackage object.

    Returns:
        list: Containing MarkingSpecification objects.
    """
    from . import navigator

    _load_stix()
    null_markings = []

    for entity in navigator.iterwalk(package):
        if isinstance(entity, stix_dm.MarkingSpecification):
            if not entity.controlled_structure:
                null_markings.append(entity)

    return null_markings
