# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.


class MissingMarkingPathError(Exception):
    def __init__(self, message, entity):
        super(MissingMarkingPathError, self).__init__(message)
        self.entity = entity


class UnrecognizedMarkingPathError(Exception):
    def __init__(self, message, entity, path):
        super(UnrecognizedMarkingPathError, self).__init__(message)
        self.entity = entity
        self.path = path


class UnknownMarkingError(Exception):
    def __init__(self, message, marking):
        super(UnknownMarkingError, self).__init__(message)
        self.marking = marking


class DuplicateMarkingError(Exception):
    def __init__(self, message, entity, marking):
        super(DuplicateMarkingError, self).__init__(message)
        self.entity = entity
        self.marking = marking


class UnmarkableError(Exception):
    def __init__(self, message, entity):
        super(UnmarkableError, self).__init__(message)
        self.entity = entity


class InvalidRootError(Exception):
    def __init__(self, message, entity):
        super(InvalidRootError, self).__init__(message)
        self.entity = entity


class IdLookupError(Exception):
    def __init__(self, message, id_):
        super(IdLookupError, self).__init__(message)
        self.id_ = id_


class InvalidModeError(Exception):
    def __init__(self, message, found, expected):
        super(InvalidModeError, self).__init__(message)
        self.found = found
        self.expected = expected


class MarkingNotFoundError(Exception):
    def __init__(self, message, entity, marking):
        super(MarkingNotFoundError, self).__init__(message)
        self.entity = entity
        self.marking = marking


class MarkingPathNotEmpty(Exception):
    def __init__(self, message, marking):
        super(MarkingPathNotEmpty, self).__init__(message)
        self.marking = marking


class MarkingRemovalError(Exception):
    def __init__(self, message, entity, marking):
        super(MarkingRemovalError, self).__init__(message)
        self.entity = entity
        self.marking = marking


class SerializerMappingError(Exception):
    def __init__(self, message, entity):
        super(SerializerMappingError, self).__init__(message)
        self.entity = entity


class SerializerFieldNotFoundError(Exception):
    def __init__(self, message, entity):
        super(SerializerFieldNotFoundError, self).__init__(message)
        self.entity = entity
