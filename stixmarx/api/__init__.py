# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

"""
This module defines methods for applying and retrieving data markings.
"""

# internal
from stixmarx.api import types
from stixmarx import errors
from stixmarx import utils


_ATTR_DATA_MARKINGS = "__datamarkings__"


def _attach(markable, marking):
    """Attach the MarkingSpecification object `marking` to the `markable` object.

    If `markable` does not have a __datamarkings__ collection, one will be
    created and set.

    Args:
        markable: An object that can accept data marking information.
        marking: A python-stix MarkingSpecification object.
    """
    if not hasattr(markable, _ATTR_DATA_MARKINGS):
        markable.__datamarkings__ = set()
    markable.__datamarkings__.add(marking)


def _assert_markable(m):
    """Assert that the input can have data markings attached to it.

    Args:
        m: An object.

    Raises:
        errors.UnmarkableError: If the input object `m` cannot be marked.
    """
    if is_markable(m):
        return

    error = "Input type %s is not markable." % type(m)
    raise errors.UnmarkableError(error, m)


def is_markable(m):
    """Return True if the input object `m` can be marked.

    Markable objects are:
    * Anything that has a __datamarkings__ attribute.
    * Entity instances (mixbox or python-stix)
    * Builtin scalar types that are castable via the stixmarx.api.types module

    Note:
        Though types.is_castable() will return True for lists that contain
        only castable builtin objects, lists or other iterable collections
        are not markable.

    Args:
        m: An object.

    Returns:
        True if the input object is markable. False otherwise.
    """
    if hasattr(m, _ATTR_DATA_MARKINGS):
        return True
    elif utils.is_entity(m):
        return True
    elif utils.is_sequence(m):
        return False
    else:
        return types.is_castable(m)


def is_marked(markable):
    """Return True if the input `markable` object contains data markings.

    Args:
        markable: An object.
    """
    return bool(getattr(markable, _ATTR_DATA_MARKINGS, False))


def contains_marking(markable, marking):
    """Return True if the `markable` object is marked by the
    MarkingSpecification `marking` object.

    Args:
        markable: A marked object.
        marking: A MarkingSpecification object.
    """
    markings = get_markings(markable)

    if not markings:
        return False

    return marking in markings


def get_markings(markable):
    """Return the collection of data markings attached to the input `markable`
    object.

    Args:
        markable: A marked object.

    Returns:
        None if the object is not marked. A tuple of data markings if `markable`
        is marked.
    """
    if not is_marked(markable):
        return tuple()
    return tuple(markable.__datamarkings__)


def add_markings(markable, markings):
    """Add multiple markings to the `markable` object.

    Note:
        If `markable` is an immutable Python type, the user will need to replace
        the input value with the return value:

        >>> i = Indicator(id_"foo")
        >>> new_id = add_marking(i.id_, MARKING)
        >>> i.id_  = new_id
        >>>
        >>> # OR do it in one line
        >>>
        >>> i.id_ = add_marking(i.id_, MARKING)

    Args:
        markable: A markable object.
        markings: An iterable collection of MarkingSpecification objects.

    Returns:
        The input object (or a markable variant) that has been marked by the
        input `markings`. If `markable` is a Python builtin immutable type, it
        will be coerced into a new stixmarx.api.types type.

    Raises:
        errors.UnmarkableError: If the `markable` object cannot have markings
            attached to it.
    """
    for marking in markings:
        markable = add_marking(markable, marking)

    return markable


def add_marking(markable, marking):
    """Add a single marking to the `markable` object.

    Args:
        markable: A markable object.
        marking: A MarkingSpecification object.

    Returns:
        The input object (or a markable variant) that has been marked by the
        input `marking`. If `markable` is a Python builtin scalar type.

    Raises:
        errors.UnmarkableError: If the `markable` object cannot have markings
            attached to it.
    """
    _assert_markable(markable)

    if types.is_castable(markable):
        markable = types.cast(markable)

    _attach(markable, marking)

    return markable


def remove_markings(markable, markings):
    """Remove the collection of `markings` from the `markable` object. If the
    `markable` object is not marked, do nothing.

    Args:
        markable: A markable object.
        markings: An iterable collection of MarkingSpecification objects.

    Raises:
        KeyError: If `markable` is not marked by one or more of the `markings`.
    """
    for marking in markings:
        remove_marking(markable, marking)


def remove_marking(markable, marking):
    """Remove the `marking` from the `markable` object. If the `markable`
    object is not marked, do nothing.

    Args:
        markable: A markable object.
        marking: A MarkingSpecification object.

    Raises:
        KeyError: If `markable` is not marked by one or more of the `markings`.
    """
    if not is_marked(markable):
        return

    markable.__datamarkings__.remove(marking)


def clear_markings(markable):
    """Remove all marking information from the `markable` object. If `markable`
    is not marked, do nothing.

    Args:
        markable: A markable object.
    """
    if is_marked(markable):
        markable.__datamarkings__ = set()

