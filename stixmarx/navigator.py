# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

"""
This module define classes and methods that allow traversal of the object model.
"""

# builtins
import itertools

# external
from mixbox.vendor.six import iteritems

# internal
from stixmarx.utils import is_entitylist, is_skippable, attr_name, is_sequence


class Navigator(object):
    """Enables walking the Python object model. Although, similar to STIX
    iterwalk and iterpath methods, it only walks through mixbox.entities.Entity
    objects.

    The Navigator avoids walking through the __datamarkings__ collection.
    Which may cause an infinite loop in older approaches that walk the
    object model when markings are present.

    Note:
        A Navigator instance should not be created directly. Instead, use
        navigator.iterwalk() or navigator.iterpath() to create the corresponding
        generators.

    """
    def __init__(self):
        pass

    @staticmethod
    def _iter_fields(obj):
        attrs = []

        if hasattr(obj, "_fields"):
            attrs.append(iteritems(obj._fields))

        if hasattr(obj, "__dict__"):
            attrs.append(iteritems(vars(obj)))

        return itertools.chain.from_iterable(attrs)

    def iterwalk(self, entity):
        def yield_and_walk(item):
            if item is None:
                return

            yield item

            for descendant in self.iterwalk(item):
                yield descendant

        for varname, varobj in self._iter_fields(entity):
            if is_skippable(entity, varname, varobj):
                continue

            if is_sequence(varobj) and not is_entitylist(varobj):
                for item in varobj:
                    if is_skippable(varobj, varname, item):
                        continue
                    for descendant in yield_and_walk(item):
                        yield descendant

                continue

            for descendant in yield_and_walk(varobj):
                yield descendant

    def iterpath(self, obj, path=None):
        def yield_and_descend(name, item):
            yield (path, attr_name(path, name), item)

            if item is None:
                return

            for path_info in self.iterpath(item, path):
                yield path_info

        if path is None:
            path = []

        path.append(obj)

        for varname, varobj in self._iter_fields(obj):
            if is_skippable(obj, varname, varobj):
                continue

            if is_sequence(varobj) and not is_entitylist(varobj):
                for item in varobj:
                    for path_info in yield_and_descend(varname, item):
                        yield path_info

            else:
                for path_info in yield_and_descend(varname, varobj):
                    yield path_info

        path.pop()


def iterwalk(entity):
    """Returns an generator which `walks` the input object model. Each
    iteration yields a mixbox.entities.Entity or Python built-in children
    of `entity`.

    This is performed depth-first.

    Args:
        entity: A mixbox.entities.Entity

    Yields:
        Children of `entity`.
    """
    navigator = Navigator()

    for field in navigator.iterwalk(entity):
        yield field


def iterpath(entity):
    """Returns a generator which `walks` the input object model. Each
    iteration yields a triple containing a list of ancestor nodes, the name
    of the field, and the field value.

    This is performed depth-first.

    Args:
        entity: A mixbox.entities.Entity

    Example:
        An Indicator Title with a value of "Test" could be yielded as follows:
        ([STIXPackage, Indicators, Indicator], "title", "Test")

    Yields:
        tuple: Containing three items.
    """
    navigator = Navigator()

    for field in navigator.iterpath(entity):
        yield field
