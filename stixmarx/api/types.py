# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# stdlib
import datetime

# external
from mixbox import dates
from mixbox.vendor import six
from mixbox.vendor.six import text_type, binary_type

# internal
from stixmarx import utils

if six.PY3:
    long = int


class MarkableBool(int):
    """Python `bool` cannot be subclassed directly.
    This class subclasses `int` (just as `bool` does)
    and behaves like a `bool`.
    """

    def __init__(self, value):
        super(MarkableBool, self).__init__()
        self.__datamarkings__ = set()

    def __new__(cls, value):
        return int.__new__(cls, bool(value))

    def __repr__(self):
        return str(bool(self))


class MarkableInt(int):
    def __init__(self, value):
        super(MarkableInt, self).__init__()
        self.__datamarkings__ = set()

    def __new__(cls, value):
        return int.__new__(cls, value)


class MarkableLong(long):
    def __init__(self, value):
        super(MarkableLong, self).__init__()
        self.__datamarkings__ = set()

    def __new__(cls, value):
        return long.__new__(cls, value)


class MarkableFloat(float):
    def __init__(self, value):
        super(MarkableFloat, self).__init__()
        self.__datamarkings__ = set()

    def __new__(cls, value):
        return float.__new__(cls, value)


class MarkableDateTime(datetime.datetime):
    def __init__(self, value):
        super(MarkableDateTime, self).__init__()
        self.__datamarkings__ = set()

    def __new__(cls, value):
        dt = dates.parse_datetime(value)

        return datetime.datetime.__new__(
            cls,
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            tzinfo=dt.tzinfo
        )


class MarkableDate(datetime.date):
    def __init__(self, value):
        super(MarkableDate, self).__init__()
        self.__datamarkings__ = set()

    def __new__(cls, value):
        dt = dates.parse_date(value)

        return datetime.date.__new__(
            cls,
            year=dt.year,
            month=dt.month,
            day=dt.day
        )


class MarkableBytes(binary_type):
    def __init__(self, value):
        super(MarkableBytes, self).__init__()
        self.__datamarkings__ = set()

    def __new__(cls, value):
        value = value or ""
        return binary_type.__new__(cls, value)


class MarkableText(text_type):
    def __init__(self, value):
        super(MarkableText, self).__init__()
        self.__datamarkings__ = set()

    def __new__(cls, value):
        value = value or ""
        return text_type.__new__(cls, value)


if six.PY2:
    TYPEMAP = {
        bool: MarkableBool,
        int: MarkableInt,
        float: MarkableFloat,
        long: MarkableLong,
        binary_type: MarkableBytes,
        text_type: MarkableText,
        datetime.datetime: MarkableDateTime,
        datetime.date: MarkableDate
    }
else:
    TYPEMAP = {
        bool: MarkableBool,
        int: MarkableInt,
        float: MarkableFloat,
        binary_type: MarkableBytes,
        text_type: MarkableText,
        datetime.datetime: MarkableDateTime,
        datetime.date: MarkableDate
    }


def is_castable(obj):
    """Return True if the input `obj` can be casted to a markable datatype.

    If `obj` is a list, this will check that each member of the list is
    castable.
    """
    if utils.is_list(obj):
        return all(type(x) in TYPEMAP for x in obj)
    else:
        return type(obj) in TYPEMAP


def cast(input_):
    """Convert the castable `input` object into a markable object.

    Args:
        input_: A castable object or a list of castable objects.

    Returns:
        A markable conversion of the `input` object. E.g., A `str` object will
        become a MarkableString object.
    """
    if utils.is_list(input_):
        return [cast(x) for x in input_]

    type_ = type(input_)
    klass = TYPEMAP[type_]
    return klass(input_)
