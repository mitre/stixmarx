# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

from lxml import etree

# Namespaces
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS_XML_SCHEMA = "http://www.w3.org/2001/XMLSchema"

# LXML QNAMES TAGS
TAG_XS_INCLUDE = "{%s}include" % NS_XML_SCHEMA
TAG_XS_IMPORT = "{%s}import" % NS_XML_SCHEMA
TAG_XSI_TYPE = "{%s}type" % NS_XSI
TAG_SCHEMALOCATION = "{%s}schemaLocation" % NS_XSI

# Global selectors
XPATH_GLOBAL_ALL_ELEMS = "//node()"
XPATH_GLOBAL_ALL_ATTRS = "//@*"
XPATH_GLOBAL_ALL_FIELDS = "{0} | {1}".format(
    XPATH_GLOBAL_ALL_ELEMS,
    XPATH_GLOBAL_ALL_ATTRS
)

# Selectors relative to a TLO (top-level object)
XPATH_TLO_RELATIVE_START = "../../.."

# Selectors relative to a marking at the STIX Header object.
XPATH_HEADER_RELATIVE_START = "../../../.."

# Axis for nodes
XPATH_AXIS_SELF_NODE = "self::node()"
XPATH_AXIS_DESCENDANT_OR_SELF_NODE = "descendant-or-self::node()"

# Operators
XPATH_JOIN_OPERATOR = "{0} | {1}"
XPATH_SELECT_OPERATOR = "/"

# Selectors
XPATH_WILDCARD_ALL_ATTRS = "@*"

# Node selection structure
XPATH_STRUCTURE = "{prefix}:{nodename}[{predicates}]"


def is_element(node):
    """Return True if the input `node` is an XML element node."""
    return etree.iselement(node)


def is_attribute(node):
    """Return True if the input `node` is an XML attribute node."""
    if hasattr(node, 'is_attribute'):
        return node.is_attribute
    return False


def is_content(node):
    """Return True if the input `node` is a text node."""
    return ((isinstance(node, etree._ElementStringResult) or
            isinstance(node, etree._ElementUnicodeResult)) and
            not is_attribute(node))


def is_typed(node):
    """Return True if the `node` has a an xsi:type attribute."""
    if hasattr(node, 'attrib'):
        return TAG_XSI_TYPE in node.attrib
    return False


def xsitype_ns(node):
    """Return the datatype namespace for the input xsi:typed node.

    Args:
        node: An lxml etree Element node.

    Returns:
        The value of the input `node` @xsi:type attribute or None if no
        @xsi:type attribute is found.
    """
    if not is_typed(node):
        return None

    xsi_type = node.attrib[TAG_XSI_TYPE]
    alias = xsi_type.split(":")[0]
    namespace = node.nsmap[alias]
    return namespace


def is_etree(tree):
    """Return ``True`` if `tree` is an lxml etree ElementTree object."""
    return isinstance(tree, etree._ElementTree)


def to_etree(doc, encoding=None):
    """Return the `doc` as an ElementTree object.

    Args:
        doc: A filename, file-like object, or etree object (Element/ElementTree).
        encoding: The file encoding.

    Returns:
        An etree ElementTree object.
    """
    if is_etree(doc):
        return doc
    elif etree.iselement(doc):
        return etree.ElementTree(doc)
    else:
        parser = get_xml_parser(encoding=encoding)
        return etree.parse(doc, parser=parser)


def root(doc, encoding=None):
    """Return the root node for the input XML `doc`.

    Args:
        doc: A read()-able XML document, etree ElementTree or Element object.
        encoding: The encoding of the input document.

    Returns:
        An lxml Element object for the root of the input `doc`.
    """
    tree = to_etree(doc, encoding)
    return tree.getroot()


def get_xml_parser(encoding=None):
    """Returns an ``etree.ETCompatXMLParser`` instance."""
    parser = etree.ETCompatXMLParser(
        huge_tree=True,
        remove_comments=True,
        strip_cdata=False,
        remove_blank_text=True,
        resolve_entities=False,
        encoding=encoding
    )

    return parser


def localname(node):
    """Return the XML localname for the input lxml `node`.

    Args:
        node: An lxml etree element/attribute node.

    Returns:
        A string XML localname.
    """
    if is_attribute(node):
        return etree.QName(node.attrname).localname
    else:
        return etree.QName(node).localname


def find(node, localname):
    """Find the first element under `node` with a matching localname.

    Args:
        node: An lxml etree Element object.
        localname: An XML localname for an element.

    Returns:
        An lxml etree Element object if found or None if not found.
    """
    xmltag = "{*}%s" % localname
    return node.find(xmltag)


def findall(node, localname):
    """Find all elements under `node` with a matching localname.

    Args:
        node: An lxml etree Element object.
        localname: An XML localname for an element.

    Returns:
        An iterable collection of  lxml etree Element objects.
    """
    if localname == "text()":
        # Fixes @delimiter separated values. We need a _ElementStringResult in
        # order to perform the correct matching.
        return node.xpath(localname)

    xmltag = "{*}%s" % localname
    return node.findall(xmltag)


def findattr(node, attrname):
    """Find the attribute under `node` with a matching attribute name.

    Args:
        node: An lxml etree Element object.
        attrname: An XML attribute name.

    Returns:
        An lxml etree ElementStringResults object if found or None if not found.
    """
    if not attrname.startswith("@"):
        attrname = "@%s" % attrname
    return next(iter(node.xpath(attrname)), None)


def findtext(node):
    """Return the text() node for the input `node` or None if no text() is
    found.

    Args:
        node: An lxml etree Element node.
    """
    return next(iter(node.xpath("text()")), None)
