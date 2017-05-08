# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

"""
This version of the API can operate on major components and fields of
STIX, CybOX and MAEC entities. Acting on anything not classified as an
"entity" per the above definition is not supported and will raise an exception.
When API functions say they accept a "markings" object, it means they accept a
MarkingSpecification object, not a MarkingStructure. If you have a
MarkingStructure you wish to use to mark something, you must first place it
inside a MarkingSpecification object and supply that object to the API.
"""

# stdlib
import collections
import itertools

# internal
from stixmarx import api
from stixmarx import errors
from stixmarx import navigator
from stixmarx import serializer
from stixmarx import utils

__all__ = ['MarkingContainer']


class MarkingContainer(object):
    """Enables the operation of data markings on STIX, CybOX and MAEC objects.
    
    A MarkingContainer provides interfaces for applying, accessing, clearing
    and removing data marking information from its wrapped STIX Package. A
    MarkingContainer has methods for processing marking information and
    serialization which translate the marked object model into XPath
    controlled structures.

    Note:
        A MarkingContainer should not be created directly. Instead, use
        stixmarx.parse() or stixmarx.new() to create MarkingContainer instances.

    Attributes:
        package (stix.core.STIXPackage): The package object (from python-stix)
            wrapped by this container.
        global_markings (list of MarkingSpecification): List of markings that
            apply to the container `package` as a whole (every descendant).
        field_markings (dict, maps markable objects to MarkingSpecification):
            Dictionary where keys are `markable` entities and the values are a
            `list` that contain tuples of MarkingSpecification and descendants
            (True/False) option.
        null_markings: (list of MarkingSpecification): List of markings that
            apply to this container but, will NOT mark anything inside. This
            means, no controlled structure will be resolved for this objects.
    """

    def __init__(self, package):
        """Initialize a MarkingContainer object.

        Args:
            package: A stix.core.STIXPackage object.
        """
        self._field_markings = collections.defaultdict(list)
        self._global_markings = []
        self._null_markings = []

        self._package = package

    def _reset_collections(self):
        self._field_markings = collections.defaultdict(list)
        self._global_markings = []
        self._null_markings = []

    @property
    def global_markings(self):
        """Return the global markings that have been set via add_global().

        Note:
            This property DOES NOT return markings that were applied by
            MarkingParser (even markings that were applied to all nodes in the
            parsed document).

        Returns:
            tuple: Tuple containing MarkingSpecification objects.
        """
        return tuple(self._global_markings)

    @property
    def null_markings(self):
        """Return the null markings that have been set via add_markings().
        Where `markable` is None.

        Note:
            This property DOES NOT return markings that were applied by
            MarkingParser.

        Returns:
            tuple: Tuple containing MarkingSpecification objects.
        """
        return tuple(self._null_markings)

    @property
    def field_markings(self):
        """Return the field markings that have been set via add_marking().

        Note:
            This property DOES NOT return markings that were applied by
            MarkingParser.

        Returns:
            dict: Dictionary where keys are `markable` entities and values are
            a list of tuples with MarkingSpecification objects and their
            corresponding (True/False) descendants option.
        """
        return dict(self._field_markings)

    @property
    def package(self):
        """Package wrapped by this MarkingContainer"""
        return self._package

    def _add_descendants(self, markable, marking):
        """Apply marking to `markable` in-place to descendants."""
        for descendant in navigator.iterwalk(markable):
            descendant = api.add_marking(descendant, marking)

    def _remove_descendants(self, markable, marking):
        """Remove marking from the `markable` descendants."""
        for descendant in navigator.iterwalk(markable):
            if api.contains_marking(descendant, marking):
                api.remove_marking(descendant, marking)

    def _clear_descendants(self, markable):
        """Clear markings from the `markable` descendants."""
        for descendant in navigator.iterwalk(markable):
            api.clear_markings(descendant)

    def _get_descendants(self, markable):
        """Return unique markings from the `markable` descendants."""
        uniques = set()
        for descendant in navigator.iterwalk(markable):
            markings = api.get_markings(descendant)
            if markings:
                uniques.update(markings)

        return uniques

    def _remove_marking_specification(self, marking):
        """Removes MarkingSpecification object from the object model."""
        for descendant in navigator.iterwalk(self._package):
            if hasattr(descendant, "handling") and descendant.handling:
                if marking in descendant.handling:
                    descendant.handling.remove(marking)
                    return

        msg = "Unable to remove marking from document: marking not found."
        raise errors.MarkingNotFoundError(message=msg, entity=self.package,
                                          marking=marking)

    def _assert_unique_marking(self, markable, marking):
        """Assert that the input `markable` object is not marked by `marking`.
        If `markable` is already marked by `marking`, raise an error.

        Raises:
            errors.DuplicateMarkingError: If `markable` is already marked by
                `marking`.
        """
        is_duplicate = self.is_marked(markable, marking=marking)

        if not is_duplicate:
            return

        msg = ("The entity is already marked with this marking or an "
               "equivalent marking.")

        raise errors.DuplicateMarkingError(message=msg, entity=markable,
                                           marking=marking)

    def add_marking(self, markable, marking, descendants=False):
        """Add the `marking` to the `markable` field/object. If `markable`
        is a built-in immutable Python type, it will be coerced into a
        stixmarx.api.types datatype.

        Note:
            The add_marking() function may not always be able to apply the
            markings in-place. Users should set the input field to the return
            object after calling add_marking().

        Note:
            Use this method to apply null markings. This is, markings that are
            present within the document but, do not apply to any field. The
            `markable` parameter MUST be None.

        Example:
            >>> print type(indicator.title)
            <type 'str'>
            >>> marked_title = add_marking(indicator.title, marking)
            >>> print type(marked_title)
            <class 'stixmarx.api.types.MarkableBytes'>
            >>> indicator.title = marked_title  # set the title to the return value

        Example:
            >>> print type(indicator.timestamp)
            <type 'datetime.datetime'>
            >>> marked_timestamp = add_marking(indicator.timestamp, marking)
            >>> print type(marked_timestamp)
            <class 'stixmarx.api.types.MarkableDateTime'>
            >>> indicator.timestamp = marked_timestamp # set timestamp to the return value

        Example:
            >>> print type(indicator)
            <class 'stix.indicator.indicator.Indicator'>
            >>> marked_indicator = add_marking(indicator, marking, descendants=True) # The equivalent of a component marking
            >>> print type(marked_indicator)
            <class 'stix.indicator.indicator.Indicator'>
            >>> indicator = marked_indicator


        Args:
            markable: An object to mark (e.g., an Indicator.title string).
            marking: A python-stix MarkingSpecification object.
            descendants: If true, add the marking to all descendants
                `markable`.

        Returns:
            The `markable` object with data marking information attached. If
            `markable` is a built-in immutable Python type (e.g., str), it will
            be changed to a stixmarx.api.types datatype.

        Raises:
            UnmarkableError: If `markable` is a STIXPackage object.
            DuplicateMarkingError: If `markable` is already marked by
                `marking`.
            MarkingPathNotEmpty: If `marking` controlled_structure is set.
        """
        utils.check_marking(marking)
        utils.check_empty_marking(marking)

        # Handles null marking case.
        if markable is None:
            if marking not in self._null_markings:
                self._null_markings.append(marking)
                return
            else:
                msg = ("The marking is already present in the null_markings"
                       " internal collection.")

                raise errors.DuplicateMarkingError(message=msg,
                                                   entity=self.package,
                                                   marking=marking)

        self._assert_unique_marking(markable, marking)

        # API call before to avoid duplicates.
        marked = api.add_marking(markable, marking)

        if not utils.is_package(markable):
            if all((marking, descendants) != mark
                   for mark in self._field_markings[marked]):

                if descendants:
                    self._add_descendants(markable, marking)

                # Store marking and descendants option tied.
                self._field_markings[marked].append((marking, descendants))
                return marked

            msg = ("The marking is already present in the field_markings"
                   " internal collection.")

            raise errors.DuplicateMarkingError(message=msg,
                                               entity=self.package,
                                               marking=marking)

        msg = "Cannot mark STIX Package: use add_global()"
        raise errors.UnmarkableError(entity=markable, message=msg)

    def add_global(self, marking):
        """Add the `marking` MarkingSpecification object to the set of
        globally applicable markings (markings that apply to this container's
        package and all of its descendants).

        Markings added here will be included in the set returned from
        get_markings() for any valid field.

        Args:
            marking: A MarkingSpecification object.

        Raises:
            TypeError: If `marking` is not a MarkingSpecification object.
            MarkingPathNotEmpty: If `marking` controlled_structure is set.
            DuplicateMarkingError: If `marking` is already present in
                `global_markings` collection.
        """
        utils.check_marking(marking)
        utils.check_empty_marking(marking)

        if marking not in self._global_markings:
            self._global_markings.append(marking)
            return

        msg = ("The marking is already present in the global_markings"
               " internal collection.")

        raise errors.DuplicateMarkingError(message=msg,
                                           entity=self.package,
                                           marking=marking)

    def flush(self):
        """Flush markings onto package object.

        Markings are buffered in the MarkingContainer until explicitly flushed
        out to the MarkingContainer's package through this method.

        Note:
            The global and fields collection will reset after this call.

        Returns:
            stix.core.STIXPackage: A STIX Package with all makings explicitly
                applied from the container.
        """
        writer = serializer.MarkingSerializer(marking_container=self)
        writer._apply_markings()

        # Reset the collections so we don't return duplicates
        self._reset_collections()

        return self.package

    def get_markings(self, markable, descendants=False, null_markings=False):
        """Return the markings associated with the input `markable` object.

        Note:
            This will include any global markings that have not been explicitly
            applied to this field.

        Args:
            markable: A markable object (e.g., indicator.title).
            descendants: If True, return markings which apply to the input
                field and all of its descendants.
            null_markings: If True, return internal markings that do NOT apply
                to any markable. This null markings have not been explicitly
                set to the wrapped document. Use utils.get_null_markings(...)
                to find null markings that have been explicitly set in the
                document.

        Returns:
            list: A list of MarkingSpecification objects.
        """
        item_markings = api.get_markings(markable)
        descendant_markings_collection = ()
        null_markings_collection = ()

        if descendants:
            descendant_markings_collection = self._get_descendants(markable)

        if null_markings:
            null_markings_collection = self._null_markings

        all_markings = itertools.chain(
            self._global_markings,
            item_markings,
            descendant_markings_collection,
            null_markings_collection
        )

        return list(set(all_markings))

    def is_marked(self, markable, marking=None, descendants=False):
        """Return True if `markable` contains marking information.

        Args:
            markable: An markable object.
            marking: A MarkingSpecification object.
            descendants: If set, inspect descendant fields for marking
                information.

        Raises:
            UnmarkableError: If `markable` is not an markable entity.
            UnknownMarkingError: If `marking` is not a MarkingSpecification
                object.

        Returns:
            bool: True under the following conditions: if `markable` contains
                marking information, if `markable` is marked by `marking`, if
                `markable` descendants contain markings or if global markings
                have been added through add_global(). Otherwise False.
        """
        if api.is_markable(markable):
            markings = self.get_markings(markable, descendants)

            if marking is not None:
                utils.check_marking(marking)
                return marking in markings

            return bool(markings)

        msg = "Could not verify markings to unmarkable entity."
        raise errors.UnmarkableError(entity=markable, message=msg)

    def remove_marking(self, markable, marking, descendants=False):
        """Remove the `marking` MarkingSpecification from `markable`.

        Note:
            Use remove_global to remove globally applied markings.

        Args:
            markable: An object which contains data markings.
            marking: A MarkingSpecification object.
            descendants: If True, remove `marking` from any descendants.

        Raises:
            UnmarkableError: If `markable` is not an markable entity.
            MarkingNotFoundError: If `markable` (or descendant of `markable` if
                `descendants` is True) is marked by `marking`. If marking was
                not found in the internal marking collection.
            MarkingRemovalError: If `marking` is inherited from an ancestor OR
                if `markable` is STIXPackage object.
            UnknownMarkingError: If `marking` is not a MarkingSpecification
                object.
        """
        utils.check_marking(marking)

        # Handles null marking case.
        if markable is None:
            # Attempt to remove null marking from internal collection.
            if marking in self._null_markings:
                try:
                    self._null_markings.remove(marking)
                    return
                except (AttributeError, ValueError):
                    msg = ("Unable to remove marking from internal null"
                           " marking collection. Marking not found.")
                    raise errors.MarkingNotFoundError(entity=markable,
                                                      message=msg,
                                                      marking=marking)
            # Attempt to remove null marking from wrapped STIX Package.
            else:
                self._remove_marking_specification(marking)
                return

        if api.is_markable(markable):

            # Attempt to remove field-level marking from internal collection.
            if markable in self._field_markings:
                field_markings = self._field_markings[markable]

                try:
                    field_markings.remove((marking, descendants))
                    self._field_markings[markable] = field_markings

                    if api.contains_marking(markable, marking):
                        api.remove_marking(markable, marking)

                        if descendants:
                            self._remove_descendants(markable, marking)

                    return
                except (AttributeError, ValueError):
                    msg = ("Unable to remove marking from internal field-level"
                           " marking collection. Marking not found.")
                    raise errors.MarkingNotFoundError(entity=markable,
                                                      message=msg,
                                                      marking=marking)

            # Attempt to remove marking from wrapped STIX Package.
            elif api.contains_marking(markable, marking):

                if utils.is_package(markable):
                    msg = ("Cannot remove marking from STIX Package: use"
                           " remove_global()")
                    raise errors.MarkingRemovalError(entity=markable,
                                                     message=msg,
                                                     marking=marking)

                for mark in navigator.iterwalk(self._package):
                    if api.contains_marking(mark, marking):
                        if mark is markable:
                            api.remove_marking(markable, marking)

                            if descendants:
                                self._remove_descendants(markable, marking)

                            self._remove_marking_specification(marking)

                            return
                        else:
                            msg = ("Unable to remove marking. Marking is "
                                   "inherited from an ancestor.")
                            raise errors.MarkingRemovalError(message=msg,
                                                             entity=markable,
                                                             marking=marking)

            msg = "Unable to remove marking from markable. Marking not found."
            raise errors.MarkingNotFoundError(entity=markable, message=msg,
                                              marking=marking)

        msg = "Could not remove markings to unmarkable entity."
        raise errors.UnmarkableError(entity=markable, message=msg)

    def clear_markings(self, markable, descendants=False):
        """Remove all markings from the `markable` marked object.

        Args:
            markable: A marked object (e.g., indicator.title)
            descendants: If True, clear markings from `markable` and
                its descendants.

        Raises:
            UnmarkableError: If `markable` is not an markable entity.
        """
        if api.is_markable(markable):
            api.clear_markings(markable)

            if descendants:
                self._clear_descendants(markable)

            return

        msg = "Could not clear markings to unmarkable entity."
        raise errors.UnmarkableError(entity=markable, message=msg)

    def remove_global(self, marking):
        """Remove a globally-applied marking from the internal collection or
        from a parsed document that contain globally-applied markings.

        Args:
          marking (MarkingSpecification): marking to un-apply from global

        Raises:
            MarkingNotFoundError: If `marking` is not found in the
                global markings registry.
        """
        utils.check_marking(marking)

        # Attempt to remove marking from internal collection
        if marking in self._global_markings:
            try:
                self._global_markings.remove(marking)
                return
            except (AttributeError, ValueError):
                pass

        # Attempt to remove marking from wrapped STIX package.
        else:
            global_markings = self.get_markings(self._package)

            if marking in global_markings:
                try:
                    api.remove_marking(self._package, marking)
                    self._remove_descendants(self._package, marking)
                    self._remove_marking_specification(marking)
                    return
                except (AttributeError, ValueError):
                    pass

        msg = ("MarkingSpecification not found in global markings internal"
               " collection or in the wrapped STIX Package.")
        raise errors.MarkingNotFoundError(marking=marking, message=msg,
                                          entity=self._global_markings)

    def to_xml(self, *args, **kwargs):
        """Return an XML string of the STIX package represented by the Package
        object, with markings applied through the MarkingContainer.
        
        Uses the same arguments as ``stix.Entity.to_xml()``.
        """
        writer = serializer.MarkingSerializer(marking_container=self)
        xml_out = writer.serialize_xml(*args, **kwargs)

        # Reset the collections so duplicates aren't returned
        self._reset_collections()

        return xml_out

    def to_dict(self, *args, **kwargs):
        """Return a dictionary of the STIX Package represented by the Package
        object, with markings applied through the MarkingContainer.

        Uses the same arguments as ``stix.Entity.to_dict()``.
        """
        writer = serializer.MarkingSerializer(marking_container=self)
        dict_out = writer.serialize_dict(*args, **kwargs)

        # Reset the collections so duplicates aren't returned
        self._reset_collections()

        return dict_out
