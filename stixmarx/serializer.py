# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# builtins
import copy
import logging

# external
from mixbox.vendor.six import iteritems

# internal
from stixmarx import attrmap
from stixmarx import errors
from stixmarx import navigator
from stixmarx import utils
from stixmarx import xml

# Module-level logger
LOG = logging.getLogger(__name__)


class MarkingSerializer(object):
    """Enables the serialization of markable content by creating XPath
    expressions that assert the resulting XML. Provides support for global
    markings, that is, markings that cover the entire package. Component
    markings, these cover an entity (typically a TLO) and all of its
    descendants. Field markings provides the most granular approach to mark
    specific content like: individual elements, attributes or text of XML.

    Note:
        This class is only used internally with MarkingContainer.

    Attributes:
        container: A MarkingContainer object.
        nsmap: A dictionary with the namespace to prefix map of STIX, CybOX and
            MAEC.

    """
    def __init__(self, marking_container):
        self._container = marking_container
        self._nsmap = utils.load_nsmap()

    def _apply_global_markings(self):
        package = self._container.package
        global_markings = self._container._global_markings

        if not global_markings:
            return

        handling = utils.get_handling(package)

        for marking in global_markings:
            marking = copy.deepcopy(marking)
            marking.controlled_structure = xml.XPATH_GLOBAL_ALL_FIELDS

            handling.add_marking(marking)

    def _apply_markings_to_field(self, field, marking_info):
        """Resolves XPath and Handling for the marking. It covers component and
        field markings.

        Args:
            field: A `markable` entity.
            marking_info: Tuple, contains MarkingSpecification object and
                True/False value to indicate if marking applies to descendants.
        """
        for marking, descendants in marking_info:
            marking = copy.deepcopy(marking)
            marking.controlled_structure, handling =\
                self._find_path_and_handling(field, descendants)

            handling.add_marking(marking)

    def _apply_field_markings(self):
        field_markings = self._container._field_markings

        if not field_markings:
            return

        for field, markings_info in iteritems(field_markings):
            self._apply_markings_to_field(field, markings_info)

    def _apply_null_markings(self):
        package = self._container.package
        null_markings = self._container._null_markings

        if not null_markings:
            return

        handling = utils.get_handling(package)

        for marking in null_markings:
            marking = copy.deepcopy(marking)
            handling.add_marking(marking)

    def _apply_markings(self):
        self._apply_global_markings()
        self._apply_field_markings()
        self._apply_null_markings()

    def serialize_xml(self, *args, **kwargs):
        """
        Applies the MarkingSpecification objects from global_markings and
        field makings from the MarkingContainer.

        Args:
            *args: Arguments from ``stix.Entity.to_xml()``.
            **kwargs: Keyword arguments from ``stix.Entity.to_xml()``.

        Returns:
            stix.core.STIXPackage: A STIX Package with markings explicitly
            applied.
        """
        package = self._container.package
        self._apply_markings()
        return package.to_xml(*args, **kwargs)

    def serialize_dict(self, *args, **kwargs):
        """
        Applies the MarkingSpecification objects from global_markings and
        field makings from the MarkingContainer.

        Args:
            *args: Arguments from ``stix.Entity.to_dict()``.
            **kwargs: Keyword arguments from ``stix.Entity.to_dict()``.

        Returns:
            stix.core.STIXPackage: A STIX Package with markings explicitly
            applied.
        """
        package = self._container.package
        self._apply_markings()
        return package.to_dict(*args, **kwargs)

    def _find_path_and_handling(self, field, descendants):
        """Generates an XPath expression based on the field provided. It also
        resolves `Handling` to indicate where the marking will be stored.

        Args:
            field: A `markable` entity.
            descendants: A boolean value. If True the generated XPath covers
                descendants.

        Returns:
            tuple: A Tuple containing the control structure string for the
                MarkingSpecification and the Handling object where the Marking
                will be stored.

        Raises:
            SerializerFieldNotFoundError: When a field marking was not found
                after walking the object model.
        """
        handling = None
        xpath = None
        found = False

        for entity_path in navigator.iterpath(self._container.package):
            if field is entity_path[2]:
                found = True
                ancestors = entity_path[0]
                field_name = entity_path[1]
                field_value = entity_path[2]

                ancestors, xpath, handling = self._resolve_handling(
                        ancestors,
                        field_value
                )

                for entity in ancestors:
                    index = ancestors.index(entity)
                    prefix = self._nsmap.preferred_prefix_for_namespace(
                            entity._namespace
                    )

                    mapping = self._map_to_xml(
                            index,
                            ancestors,
                            descendants,
                            field_name
                    )

                    predicate = self._resolve_xpath_predicate(
                            index,
                            ancestors,
                            field_value
                    )

                    if (attrmap.is_attribute(mapping) or
                            attrmap.is_content(mapping) or
                            utils.is_node(mapping)):
                        xpath.append(mapping)
                    else:
                        step = xml.XPATH_STRUCTURE.format(
                                prefix=prefix,
                                nodename=mapping,
                                predicates=predicate
                        )

                        xpath.append(step)

                index = len(ancestors) - 1
                mapping = self._map_to_xml(index, ancestors, descendants)

                if not (attrmap.is_attribute(xpath[-1]) or
                        attrmap.is_content(xpath[-1])):
                    xpath.append(mapping)
                break

        if not found:
            error = "Could not generate an XPath for {0}".format(field)
            raise errors.SerializerFieldNotFoundError(entity=field,
                                                      message=error)

        xpath = xml.XPATH_SELECT_OPERATOR.join(xpath)

        if xml.XPATH_AXIS_DESCENDANT_OR_SELF_NODE in xpath and descendants:
            all_attrs = xpath + xml.XPATH_SELECT_OPERATOR + xml.XPATH_WILDCARD_ALL_ATTRS
            xpath = xml.XPATH_JOIN_OPERATOR.format(xpath, all_attrs)

        return xpath, handling

    def _map_to_xml(self, index, path, descendants, field_name=None):
        """Maps Python markable entities to their equivalent XML representation
        by matching the current.

        Args:
            index: An int, keeps the index of the current object to map.
            path: A List of mixbox.entities.Entity ancestors.
            descendants: A boolean value. If True, XPath selects descendants.
            field_name: A string. The last field to map.

        Returns:
            str: A string, result of mapping the markable entity to an XML
                representation.

        Raises:
            SerializerMappingError: When a field cannot be mapped from the
                Python object model to the corresponding XML representation.
        """
        if index + 1 == len(path):
            if field_name is None and descendants is False:
                return xml.XPATH_AXIS_SELF_NODE

            elif field_name is None and descendants is True:
                return xml.XPATH_AXIS_DESCENDANT_OR_SELF_NODE

            result = attrmap.xmlfield(path[index], field_name)

            if result is not None:
                return result

            error = "Cannot find mapping for field '{0}' in '{1}'.".format(
                field_name, type(path[index]))
            raise errors.SerializerMappingError(entity=path[index],
                                                message=error)

        elif path[index]._namespace in self._nsmap:
            result = None

            for properties in path[index].typed_fields_with_attrnames():
                attr = properties[0]

                val = getattr(path[index], attr)

                if (val is path[index + 1] or
                        (utils.is_sequence(val) and path[index + 1] in val)):
                    result = attrmap.xmlfield(path[index], attr)
                    break

            if result is not None:
                return result

        error = "Cannot find mapping for field {0} in {1}.".format(
                type(path[index + 1]), type(path[index]))
        raise errors.SerializerMappingError(entity=path[index], message=error)

    def _resolve_xpath_predicate(self, index, path, last_obj=None):
        """Determines how to resolve the xpath predicate by finding the index
        of the next node using the ancestor.

        Args:
            index: An int, keeps the index of ancestor.
            path: A List of mixbox.entities.Entity ancestors.
            last_obj: A mixbox.entities.Entity object. The last field to map.

        Returns:
            int: An integer indicating the index of the XML node being mapped.
        """
        if index + 1 == len(path):
            current = path[index]
            return self._find_index_of_seq(current, last_obj)

        else:
            ancestor = path[index]
            current = path[index + 1]
            return self._find_index_of_seq(ancestor, current)

    def _resolve_handling(self, path, field_value):
        """Resolves where to place the marking based on the following factors:

        If the ancestors of the field to be do not contain a ``Handling``
        element, place the marking in the STIX_Header. Otherwise place the
        marking in the top-most TLO or in itself when a marking is placed to a
        TLO.

        Based on the handling selection, it may be necessary to remove some
        unnecessary ancestors (for TLO cases) or change the XPath start point.

        Args:
            path: A List of mixbox.entities.Entity ancestors.
            field_value: A mixbox.entities.Entity object. The last field to map.

        Returns:
            tuple: Containing three elements: list of ancestors, the XPath
                starting position and a Handling object.
        """
        for entity in path:
            if utils.contains_handling(entity):
                xpath = [xml.XPATH_TLO_RELATIVE_START]
                handling = utils.get_handling(entity)
                path = path[path.index(entity):]
                break

            elif utils.is_stix_report(entity):
                xpath = [xml.XPATH_HEADER_RELATIVE_START]
                handling = utils.get_handling(entity)
                path = path[path.index(entity):]
                break

        else:
            if utils.contains_handling(field_value):
                xpath = [xml.XPATH_TLO_RELATIVE_START]
                handling = utils.get_handling(field_value)
                path = []
            elif utils.is_stix_report(field_value):
                xpath = [xml.XPATH_HEADER_RELATIVE_START]
                handling = utils.get_handling(field_value)
                path = []
            else:
                xpath = [xml.XPATH_HEADER_RELATIVE_START]
                handling = utils.get_handling(self._container.package)

        return path, xpath, handling

    def _find_index_of_seq(self, object_, to_find):
        """Finds the corresponding positional node location of an object that
        matches the XML model and XPath predicate.

        Since XPath indexing starts at 1, all values found have an offset of 1.

        Args:
            object_: Ancestor Entity. Parent of `to_find`.
            to_find: Current object to find positional location.

        Returns:
            int: By default 1 if the Entity is not a sequence or only one
                instance exist. Otherwise the index + 1 offset.
        """
        if utils.is_sequence(object_):
            if to_find in object_:
                return object_.index(to_find) + 1

        for properties in object_.typed_fields_with_attrnames():
            attr = properties[0]

            val = getattr(object_, attr)

            if utils.is_sequence(val) and to_find in val:
                try:
                    return val.index(to_find) + 1
                except KeyError:
                    for idx, value in enumerate(val, start=0):
                        if value is to_find:
                            return idx + 1

        return 1
