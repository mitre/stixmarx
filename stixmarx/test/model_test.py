# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

import unittest
from mixbox.vendor.six import StringIO, BytesIO
from mixbox.vendor.six import iteritems

from lxml import etree

from stix.core import STIXPackage
from stix.indicator import Indicator
from stix.data_marking import MarkingSpecification, Marking
from stix.extensions.marking.tlp import TLPMarkingStructure as TLP
from cybox.core import Observable
from cybox.objects.address_object import Address
from cybox.objects import (address_object, win_executable_file_object,
                           disk_object, win_process_object,
                           network_packet_object)

from stixmarx.api import types
from stixmarx import api
from stixmarx import attrmap
from stixmarx import parser
from stixmarx import xml


class ModelMappingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        indicator = Indicator(title="Indicator 1",
                              description="Description Indicator 1")

        indicator.alternative_id = "indicator:example1"
        indicator.observables = generate_observable()

        cls.stix_package = STIXPackage()
        cls.stix_package.add_indicator(indicator)

        cls.cybox = (address_object.Address(), address_object.EmailAddress(),
                     disk_object.Disk(), win_executable_file_object.DOSHeader(),
                     win_process_object.StartupInfo(),
                     network_packet_object.NetworkPacket())

        sio = StringIO(cls.stix_package.to_xml().decode("utf-8"))
        cls.PARSER = parser.MarkingParser(sio)

        cls.msg = "For entity {0}: {1} not found in _FIELDS dictionary."

    def test_key_in_field_dictionary(self):
        """Tests if a key is present in the _FIELDS dictionary."""
        for entity in self.cybox:
            fields = entity.typed_fields()
            attrs = vars(entity.__class__)

            for field in fields:
                for attr_name, attr in iteritems(attrs):
                    if attr is field:
                        selector = attrmap.xmlfield(entity, attr_name)
                        self.assertTrue(selector, self.msg.format(entity, attr))

    def test_mapping_assertion(self):
        """Tests the mappings for objects."""
        indicator = self.stix_package.indicators[0]

        for properties in indicator.typed_fields_with_attrnames():
            attr, tf = properties
            selector = attrmap.xmlfield(indicator, attr)
            self.assertTrue(selector, self.msg.format(indicator, attr))

            if selector == "Title":
                prefix = indicator._ID_PREFIX

                cntrl = generate_control_exp(prefix, selector)
                xpath = etree.XPath(cntrl, namespaces=self.PARSER._root.nsmap)

                result = xpath(self.PARSER._root)
                self.assertEqual(len(result), 1)

                name = xml.localname(result[0])

                self.assertEqual(name, selector)
                self.assertEqual(result[0].text, getattr(indicator, attr))

                apply_markings(self.stix_package, prefix, selector)

        # re-parse the document with marking changes.
        sio = StringIO(self.stix_package.to_xml().decode("utf-8"))
        self.PARSER = parser.MarkingParser(sio)
        package = self.PARSER.parse()

        self.assertEqual(len(package.indicators), 1)

        # See if the indicator was not marked.
        indicator = package.indicators[0]
        self.assertTrue(indicator in self.PARSER._entities)
        self.assertFalse(hasattr(indicator, api._ATTR_DATA_MARKINGS))

        title = indicator.title
        self.assertTrue(isinstance(title, (types.MarkableText, types.MarkableBytes)))
        self.assertEqual(len(title.__datamarkings__), 1)


def strip_attr(attr):
    if attr.startswith("_"):

        if attr == "_id":
            return "id_"

        return attr[1:]

    return attr


def apply_markings(stix_package, prefix, selector):
    cntrl = generate_cntrl_exp(prefix, selector)
    red_marking = generate_marking_spec(generate_red_marking_struct(), cntrl)

    stix_package.indicators[0].handling = Marking(markings=red_marking)


def generate_control_exp(prefix, selector):
    return "//{0}:{1}".format(prefix, selector)


def generate_cntrl_exp(prefix, selector):
    str1 = "../../../{0}:{1}/descendant-or-self::node()".format(prefix, selector)
    str2 = "../../../{0}:{1}/descendant-or-self::node()/@*".format(prefix, selector)

    return " | ".join([str1, str2])


def generate_red_marking_struct():
    return TLP(color='RED')


def generate_marking_spec(struct, cntrl_struct):
    spec = MarkingSpecification(controlled_structure=cntrl_struct)
    spec.marking_structures.append(struct)
    return spec


def generate_observable(cybox_obj=None):
    cybox_obj = cybox_obj or Address(address_value='10.0.0.1')
    return Observable(cybox_obj)
