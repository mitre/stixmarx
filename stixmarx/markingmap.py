# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# stdlib
import logging

# external
from mixbox.vendor.six import PY2, PY3

# internal
from stixmarx import xml


if PY2:
    from collections import MutableMapping
elif PY3:
    from collections.abc import MutableMapping

# Module-level logger
LOG = logging.getLogger(__name__)

# Required for finding data-marking schema instances.
_NSMAP = {"marking": "http://data-marking.mitre.org/Marking-1"}


class _XmlElement(object):
    """Wraps an etree _Element object.

    This is used to represent XML element objects in a NodeSet collection and
    provides an interface consistent with _XmlAttribute (e.g., they both have
    a `sourcenode` attribute).

    """
    def __init__(self, node):
        self.name = xml.localname(node)
        self.sourcenode = node

    def __eq__(self, other):
        if other is self:
            return True

        try:
            return other.sourcenode is self.sourcenode
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self.sourcenode)


class _XmlAttribute(object):
    """Wraps an etree _ElementStringResult or _ElementUnicodeResult
    object which represents an XML attribute.

    An _ElementStringResult object subclasses `str` and a _ElementUnicodeResult
    object subclasses `unicode`, so any two attributes that share the same
    value will be considered equal and have equal hashes even if they belong
    to two different XML elements.

    This class exists to distinguish attributes from each other by factoring
    an attribute's parent into the equality check.

    Note: UTF-8 encoding was selected as default to provide support
        for Unicode. If a consumer utilizes a different character encoding it
        must be provided through stixmarx.parse(xml_input, encoding="...").
    """

    def __init__(self, node, encoding=None):
        self.name = xml.localname(node.attrname)
        self.parent = node.getparent()
        self.sourcenode = node
        self.encoding = "utf-8" if not encoding else encoding

    def __eq__(self, other):
        """Return True if the `other` _XmlAttribute has the same parent
        element, the same attribute name, and the same attribute value.
        """
        if other is self:
            return True

        if other.__class__ != self.__class__:
            return False

        try:
            return (other.sourcenode == self.sourcenode and
                    other.name == self.name and
                    other.parent is self.parent)
        except AttributeError as ex:
            LOG.warn(ex)
            return False

    def __hash__(self):
        return hash((self.name, self.sourcenode, self.parent))


class MarkingMap(MutableMapping):
    def __init__(self, encoding=None):
        self._inner = {}
        self._encoding = encoding

    def __delitem__(self, key):
        return self._inner.__delitem__(self._make_key(key))

    def __len__(self):
        return self._inner.__len__()

    def __iter__(self):
        return self._inner.__iter__()

    def __getitem__(self, key):
        return self._inner.__getitem__(self._make_key(key))

    def _make_key(self, node):
        if isinstance(node, (_XmlAttribute, _XmlElement)):
            return node
        elif xml.is_element(node):
            return _XmlElement(node)
        elif xml.is_attribute(node):
            return _XmlAttribute(node, self._encoding)
        elif xml.is_content(node):
            return _XmlAttribute(node, self._encoding)
        else:
            raise TypeError("Unexpected type: %s", type(node))

    def __contains__(self, item):
        """Override the super() __contains__ which may raise a TypeError from
        _make_key().
        """
        try:
            return super(MarkingMap, self).__contains__(item)
        except TypeError:
            return False

    def __setitem__(self, key, value):
        key = self._make_key(key)
        self._inner[key] = value

    def add(self, key, value):
        key = self._make_key(key)  # Reduce the amount of casting

        if key not in self:
            self[key] = set()

        self[key].add(value)

    def extend(self, key, values):
        key = self._make_key(key)   # Reduce the amount of casting

        if key not in self:
            self[key] = set()

        self[key].update(values)

    def addall(self, keys, value):
        """Add `value` to each key found in `keys`."""
        for key in keys:
            self.add(key, value)


def _get_marking_specifications(root):
    """Find all MarkingSpecificationType instances found inside
    the input document.

    Returns:
        An iterable collection of MarkingSpecificationType lxml Element
        objects.
    """
    xpath = "//marking:Marking"
    return root.xpath(xpath, namespaces=_NSMAP)


def _get_controlled_structure(spec):
    """Return the ``Controlled_Structure`` element found under the input
    `spec` MarkingSpecificationType element.

    Args:
        spec: A MarkingSpecificationType lxml element.

    Returns:
        A single ``Controlled_Structure`` lxml Element node if found. None
        if no ``Controlled_Structure`` is found.
    """
    xpath = "./marking:Controlled_Structure"
    structs = spec.xpath(xpath, namespaces=_NSMAP)

    if len(structs) == 0:
        return None

    return structs[0]


def _get_marked_nodeset(control):
    """Return the nodeset selected by the XPath defined by the input
    Controlled_Structure.

    Args:
        control: A Controlled_Structure lxml Element object.

    Returns:
        An iterable collection of lxml objects.
    """
    xpath = control.text
    namespaces = control.nsmap

    # Fixes empty namespace to prefix key->value pair when default namespace is
    # used. Note that XPath does not have a notion of a default namespace.
    # The empty prefix is therefore undefined for XPath and cannot be used in
    # namespace prefix mappings. The xpath() call can still fail if an invalid
    # xpath expression is provided.
    if None in namespaces:
        del namespaces[None]

    return control.xpath(xpath, namespaces=namespaces)


def build(root, encoding=None):
    """Build a MarkingMap which maps each element and attribute node
    found in the input document to a set of MarkingSpecificationType
    XML instances which marks them.

    The element/attribute nodes are the keys and the set of
    MarkingSpecification Element objects are the values.

    Returns:
        A stixmarx MarkingMap object.
    """
    marked = MarkingMap(encoding)
    specs = _get_marking_specifications(root)

    for spec in specs:
        control = _get_controlled_structure(spec)

        if control is None:
            continue

        nodeset = _get_marked_nodeset(control)
        marked.addall(nodeset, spec)

    return marked
