# Copyright (c) 2015, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# stdlib
import unittest

# pythons-stix
from stix import indicator
from stix import data_marking
from stix.extensions.marking import tlp

# internal
from stixmarx import api
from stixmarx import errors


MARKING = None  # defined in setUpModule()


def setUpModule():
    global MARKING

    structure = tlp.TLPMarkingStructure(color="RED")
    MARKING = data_marking.MarkingSpecification()
    MARKING.marking_structures.append(structure)


def _mark_list(lst):
    for idx, item in enumerate(lst):
        lst[idx] = api.add_marking(item, MARKING)


class CheckMarkingTests(unittest.TestCase):
    def test_is_marked(self):
        i = indicator.Indicator()
        i.__datamarkings__ = set([MARKING])
        self.assertTrue(api.is_marked(i))

    def test_is_not_marked(self):
        i = indicator.Indicator()
        self.assertFalse(api.is_marked(i))

        i.__datamarkings__ = None
        self.assertFalse(api.is_marked(i))


class AddMarkingTests(unittest.TestCase):
    def test_add_entity(self):
        i = indicator.Indicator()
        self.assertFalse(api.is_marked(i))
        api.add_marking(i, MARKING)
        self.assertTrue(api.is_marked(i))

    def test_add_list(self):
        i = indicator.Indicator()
        i.alternative_id.append("foo")
        i.alternative_id.append("bar")

        self.assertRaises(
            errors.UnmarkableError,
            api.add_marking,
            i.alternative_id,
            MARKING
        )

        _mark_list(i.alternative_id)

        self.assertEqual(i.alternative_id[0], "foo")
        self.assertEqual(i.alternative_id[1], "bar")

        self.assertTrue(api.is_marked(i.alternative_id[0]))
        self.assertTrue(api.is_marked(i.alternative_id[1]))

    def test_add_builtin(self):
        i = indicator.Indicator()
        i.id_ = "foo"

        marked = api.add_marking(i.id_, MARKING)
        self.assertEqual(marked, i.id_)
        self.assertTrue(api.is_marked(marked))


class RemoveMarkingTests(unittest.TestCase):
    def test_remove_entity(self):
        i = indicator.Indicator()
        api.add_marking(i, MARKING)

        self.assertTrue(api.is_marked(i))
        api.remove_marking(i, MARKING)
        self.assertFalse(api.is_marked(i))

    def test_not_found(self):
        i = indicator.Indicator()
        api.add_marking(i, MARKING)

        self.assertRaises(
            KeyError,
            api.remove_marking,
            i,
            data_marking.MarkingSpecification()
        )

    def test_remove_list(self):
        i = indicator.Indicator()
        i.alternative_id.append("foo")
        i.alternative_id.append("bar")

        _mark_list(i.alternative_id)

        self.assertTrue(all(api.is_marked(x) for x in i.alternative_id))

        for alt in i.alternative_id:
            api.remove_marking(alt, MARKING)

        self.assertEqual(False, all(api.is_marked(x) for x in i.alternative_id))

    def test_clear_markings(self):
        i = indicator.Indicator()
        api.add_marking(i, MARKING)

        self.assertTrue(api.is_marked(i))
        api.clear_markings(i)
        self.assertEqual(False, api.is_marked(i))

    def test_remove_builtin(self):
        i = indicator.Indicator()
        i.id_ = "foo"

        i.id_ = api.add_marking(i.id_, MARKING)
        self.assertTrue(api.is_marked(i.id_))

        api.remove_marking(i.id_, MARKING)
        self.assertEqual(False, api.is_marked(i.id_))

if __name__ == "__main__":
    unittest.main()
