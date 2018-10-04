# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# stdlib
import logging

# mixbox
from mixbox import signals

# python-stix
from stix.core import STIXPackage
from stix.data_marking import MarkingSpecification

# stixmarx
from stixmarx import api
from stixmarx import xml
from stixmarx import attrmap
from stixmarx import markingmap

# stixmarx api
from stixmarx.api import types


# Module-level logger
LOG = logging.getLogger(__name__)


# Global constants
_ATTR_SOURCENODE = "__sourcenode__"
_ATTR_BINDING = "__binding__"
_NSMAP = {"marking": "http://data-marking.mitre.org/Marking-1"}


def _binding(entity):
    """Return the __binding__ attribute value on `entity` if found or None
    if not found.

    Args:
        entity: A mixbox Entity object.
    """
    if hasattr(entity, _ATTR_BINDING):
        return entity.__binding__
    return None


def _sourcenode(entity):
    """Return the source lxml node which `entity` was created from or None
    if not found.

    Args:
        entity: A mixbox Entity object.
    """
    binding = _binding(entity)

    if binding is None:
        return None
    elif hasattr(binding, _ATTR_SOURCENODE):
        return binding.__sourcenode__
    else:
        return None


class MarkingParser(object):
    """Parses STIX XML documents and decorates STIXPackage objects with
    field-level markings.

    Attributes:
        _encoding: The encoding of the input document.
        _root: The root lxml element of the parsed input document.
        _markingmap: A MarkingMap object which associates each element/attribute
            in the input document with the Marking elements which mark them.
        _entities: A list of mixbox Entity objects that were created during
            parse().
    """

    def __init__(self, root, encoding=None):
        self._encoding = encoding
        self._root = xml.root(root, encoding)
        self._markingmap = markingmap.build(self._root, encoding)
        self._entities = list()

        # Connect our mixbox signal receiver
        signals.connect("Entity.created.from_obj", self._handle_entity_created)

    def _handle_entity_created(self, entity, binding):
        """Receiver for the mixbox Entity.created.from_obj signal.

        Attach the `binding` object to `entity` via a __binding__ attribute
        and then store `entity` in the _entities list for later processing.

        This allows us to inspect the full ancestry of `entity` since
        __binding__ has a __sourcenode__ attribute containing the lxml node
        that the __binding__ was created from:

        entity.__binding__.__sourcenode__: API-->binding-->lxml node.

        Args:
            entity: A mixbox Entity object.
            binding: The generated binding object that the `entity` was
                created from.
        """
        entity.__binding__ = binding
        self._entities.append(entity)

    def _set_list_field_marking(self, entity, attr, specs):
        """Attach marking information to each item in the list found in the
        input ``entity.attr``.

        This will also cast each value in list to a "markable" type which
        subclasses the original type. This is done via the stixmarx.types module.

        Note:
            Unmarked items in the list will not be altered in any way.

        This method is required when the API has a list attribute that holds
        a list of builtin types. This occurs when the underlying schema defines
        a flat list of builtin XSD types(e.g., "Indicator/Alternative_ID", which
        is a 0..many of xs:string).

        Args:
            entity: A mixbox Entity object.
            attr: The name of an attribute on the `entity` that has a list
                value.
            specs: A mapping of lxml MarkingSpecificationType instance nodes
                to their corresponding python-stix MarkingSpecification objects.
        """
        valuelist = getattr(entity, attr)
        node = _sourcenode(entity)
        xmlfield = attrmap.xmlfield(entity, attr)
        xmlnodes = xml.findall(node, xmlfield)
        marked = [x for x in xmlnodes if x in self._markingmap]

        for idx, val in enumerate(valuelist):
            for xmlnode in marked:
                value = valuelist[idx]
                markings = (specs[x] for x in self._markingmap[xmlnode])

                markable = api.add_markings(value, markings)
                valuelist[idx] = markable  # Replace the value in the list

    def _set_field_marking(self, entity, attr, specs):
        """Convert the `attr` attribute on `entity` to a markable type,
        attach marking information to it, and replace the original value
        with the converted, marked value.

        Note:
            If the input entity.attr is not marked, this will not perform
            any conversion or replacement.

        Args:
            entity: A mixbox Entity object.
            attr: The name of an attribute on the `entity`.
            specs: A mapping of lxml MarkingSpecificationType instance nodes
                to their corresponding python-stix MarkingSpecification objects.
        """
        node = _sourcenode(entity)
        xmlfield = attrmap.xmlfield(entity, attr)

        if attrmap.is_attribute(xmlfield):
            xmlnode = xml.findattr(node, xmlfield)
        elif attrmap.is_content(xmlfield):
            xmlnode = xml.findtext(node)
        else:
            xmlnode = xml.find(node, xmlfield)

        # If the node was not marked, do not perform any conversion or replacement.
        if xmlnode not in self._markingmap:
            return

        value = getattr(entity, attr)
        markings = (specs[x] for x in self._markingmap[xmlnode])

        markable = api.add_markings(value, markings)
        setattr(entity, attr, markable)

    def _process_attrs(self, entity, specs):
        """Attach marking information to all all non-Entity fields on `entity`
        which have been marked.

        Note:
            This will convert non-Entity attribute values to markable datatypes.
            E.g, "str" will become "MarkableBytes".

        Args:
            entity: A mixbox Entity object.
            specs: specs: A mapping of lxml MarkingSpecificationType instance
                nodes to their corresponding python-stix MarkingSpecification
                objects.
        """
        node = _sourcenode(entity)

        if node is None:
            return

        for attr in attrmap.mapping(entity):
            value = getattr(entity, attr)

            if not types.is_castable(value):
                continue
            elif isinstance(value, list):
                self._set_list_field_marking(entity, attr, specs)
            else:
                self._set_field_marking(entity, attr, specs)

    def _process_entity(self, entity, specs):
        """Attach marking information to the input `entity` if the entity has
        been marked.

        Args:
            entity: A mixbox Entity object.
            specs: specs: A mapping of lxml MarkingSpecificationType instance
                nodes to their corresponding python-stix MarkingSpecification
                objects.
        """
        node = _sourcenode(entity)

        if node not in self._markingmap:
            return

        markings = (specs[x] for x in self._markingmap[node])
        api.add_markings(entity, markings)

    def _get_marking_specification_nodemap(self):
        """Build a dictionary which maps MarkingSpecificationType XML instance
        nodes (lxml Elements) to their associated python-stix
        MarkingSpecification objects.

        Returns:
            A dictionary. The keys are lxml element nodes, and the values are
            python-stix MarkingSpecification objects.
        """
        specmap = {}
        parsed = self._entities
        specs = (x for x in parsed if isinstance(x, MarkingSpecification))

        for entity in specs:
            source = _sourcenode(entity)  # TODO (bworrell): check for None?
            specmap[source] = entity

        return specmap

    def _cleanup(self, entity):
        """Remove the __binding__ attribute we attached to the entity during
        parse. This will help reduce the memory footprint.

        Args:
            entity: A mixbox Entity object.
        """
        if _binding(entity):
            del entity.__binding__

    def _process_markings(self):
        """Attach marking information to each mixbox Entity that was created
        during ``parse()``.

        Once processed, the source __binding__ and __sourcenode__ will be
        removed from the parsed entity.

        Note:
            If a parsed Entity is not marked, no marking information or
            attributes will be attached to it.
        """
        specmap = self._get_marking_specification_nodemap()

        for entity in self._entities:
            self._process_entity(entity, specmap)
            self._process_attrs(entity, specmap)
            self._cleanup(entity)

    def parse(self):
        """Parse a STIX document and evaluate data markings found in the
        document. All marked fields will have marking information attached
        and can be queried via MarkingContainer interfaces.

        Returns:
            A STIXPackage object.
        """
        self._entities = list()  # Reset this in case of multiple parse() calls.

        # Parse the STIX Package.
        package = STIXPackage.from_xml(
            xml_file=self._root,
            encoding=self._encoding
        )

        # Attach marking information to all marked fields.
        self._process_markings()

        # Return our parsed STIXPackage.
        return package


def parse_xml(xml_input, encoding=None):
    parser = MarkingParser(root=xml_input, encoding=encoding)
    return parser.parse()
