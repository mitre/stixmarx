# Copyright (c) 2015, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

import unittest

from mixbox.vendor.six import StringIO
import stix
from stix import data_marking

from stixmarx import api
from stixmarx import parser
from stixmarx.api import types

# All of the examples in this file should be valid STIX 1.1.1 and STIX 1.2,
# so we just modify the XML based on the version of python-stix installed.
if stix.__version__ >= "1.2.0.0":
    stix_version = "1.2"
elif stix.__version__ >= "1.1.1.7":
    stix_version = "1.1.1"

XML_GLOBAL = """
<stix:STIX_Package
    xmlns:marking="http://data-marking.mitre.org/Marking-1"
    xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
    xmlns:indicator="http://stix.mitre.org/Indicator-2"
    xmlns:stix="http://stix.mitre.org/stix-1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    id="example:Package-88139233-3c7d-4913-bb5e-d2aeb079d029" version="{0}" timestamp="2015-02-26T21:00:37.453000+00:00">
    <stix:STIX_Header>
        <stix:Handling>
            <marking:Marking>
                <marking:Controlled_Structure>//node() | //@*</marking:Controlled_Structure>
                <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='GREEN'/>
            </marking:Marking>
        </stix:Handling>
    </stix:STIX_Header>
    <stix:Indicators>
        <stix:Indicator id="example:indicator1" timestamp="2015-02-26T21:00:37.454000+00:00" xsi:type='indicator:IndicatorType'>
            <indicator:Title>Indicator 1</indicator:Title>
            <indicator:Description>A Description for Indicator 1</indicator:Description>
        </stix:Indicator>
    </stix:Indicators>
</stix:STIX_Package>
""".format(stix_version)

XML_FIELDS = """
<stix:STIX_Package
    xmlns:marking="http://data-marking.mitre.org/Marking-1"
    xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
    xmlns:indicator="http://stix.mitre.org/Indicator-2"
    xmlns:stix="http://stix.mitre.org/stix-1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    id="example:Package-88139233-3c7d-4913-bb5e-d2aeb079d029" version="{0}" timestamp="2015-02-26T21:00:37.453000+00:00">
    <stix:STIX_Header>
        <stix:Handling>
            <marking:Marking>
                <marking:Controlled_Structure>//stix:Indicator[@id='example:indicator1']/@id</marking:Controlled_Structure>
                <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='RED'/>
            </marking:Marking>
            <marking:Marking>
                <marking:Controlled_Structure>//stix:Indicator[@id='example:indicator1']/indicator:Title/descendant-or-self::node()</marking:Controlled_Structure>
                <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='AMBER'/>
            </marking:Marking>
            <marking:Marking>
                <marking:Controlled_Structure>//stix:Indicator[@id='example:indicator1']/indicator:Description/descendant-or-self::node()</marking:Controlled_Structure>
                <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='GREEN'/>
            </marking:Marking>
            <marking:Marking>
                <marking:Controlled_Structure>//stix:Indicator[@id='example:indicator1']/@timestamp</marking:Controlled_Structure>
                <!-- No Marking_Structure -->
            </marking:Marking>
        </stix:Handling>
    </stix:STIX_Header>
    <stix:Indicators>
        <stix:Indicator id="example:indicator1" timestamp="2015-02-26T21:00:37.454000+00:00" xsi:type='indicator:IndicatorType'>
            <indicator:Title>Indicator 1</indicator:Title>
            <indicator:Description>A Description for Indicator 1</indicator:Description>
        </stix:Indicator>
        <stix:Indicator id="example:indicator2" xsi:type='indicator:IndicatorType'>
            <indicator:Title>NO MARKINGS</indicator:Title>
        </stix:Indicator>
    </stix:Indicators>
</stix:STIX_Package>
""".format(stix_version)

XML_LIST = """
<stix:STIX_Package
    xmlns:marking="http://data-marking.mitre.org/Marking-1"
    xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
    xmlns:indicator="http://stix.mitre.org/Indicator-2"
    xmlns:stix="http://stix.mitre.org/stix-1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    id="example:Package-88139233-3c7d-4913-bb5e-d2aeb079d029" version="{0}" timestamp="2015-02-26T21:00:37.453000+00:00">
    <stix:STIX_Header>
        <stix:Handling>
            <marking:Marking>
                <marking:Controlled_Structure>//node() | //@*</marking:Controlled_Structure>
                <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='GREEN'/>
            </marking:Marking>
        </stix:Handling>
    </stix:STIX_Header>
    <stix:Indicators>
        <stix:Indicator id="example:indicator1" timestamp="2015-02-26T21:00:37.454000+00:00" xsi:type='indicator:IndicatorType'>
            <indicator:Alternative_ID>foo</indicator:Alternative_ID>
            <indicator:Alternative_ID>bar</indicator:Alternative_ID>
        </stix:Indicator>
    </stix:Indicators>
</stix:STIX_Package>
""".format(stix_version)


class MarkingParserTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sio = StringIO(XML_GLOBAL)
        cls.PARSER = parser.MarkingParser(sio)

    def test_parse(self):
        """Smoke test."""
        package = self.PARSER.parse()

        self.assertEqual(len(package.indicators), 1)

        # See if the indicator was marked
        indicator = package.indicators[0]
        self.assertTrue(indicator in self.PARSER._entities)
        self.assertTrue(hasattr(indicator, api._ATTR_DATA_MARKINGS))

        markings = indicator.__datamarkings__
        self.assertEqual(len(markings), 1)

        spec = next(iter(indicator.__datamarkings__))
        self.assertTrue(isinstance(spec, data_marking.MarkingSpecification))

        # See if the indicator @id attribute was marked
        attr = indicator.id_
        self.assertTrue(isinstance(attr, (types.MarkableBytes, types.MarkableText)))
        self.assertEqual(len(attr.__datamarkings__), 1)

    def test_reserialize(self):
        """Test that the processed STIXPackage can still be serialized."""
        package = self.PARSER.parse()

        xml = package.to_xml()
        self.assertTrue(xml)


class FieldXMLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sio = StringIO(XML_FIELDS)
        cls.PARSER = parser.MarkingParser(sio)
        cls.PACKAGE = cls.PARSER.parse()

    def test_unmarked(self):
        unmarked = self.PACKAGE.indicators[1]
        self.assertTrue(hasattr(unmarked, "__datamarkings__") is False)
        self.assertTrue(hasattr(unmarked.title, "__datamarkings__") is False)

    def test_id_markings(self):
        i = self.PACKAGE.indicators[0]
        self.assertTrue(hasattr(i.id_, "__datamarkings__"))
        self.assertEqual(len(i.id_.__datamarkings__), 1)

        spec = next(iter(i.id_.__datamarkings__))
        struct = spec.marking_structures[0]
        self.assertEqual(struct.color, "RED")

    def test_timestamp_markings(self):
        i = self.PACKAGE.indicators[0]
        self.assertTrue(hasattr(i.timestamp, "__datamarkings__"))
        self.assertEqual(len(i.timestamp.__datamarkings__), 1)

        spec = next(iter(i.timestamp.__datamarkings__))

        # This did not have a marking structure
        self.assertEqual(len(spec.marking_structures), 0)

    def test_title_markings(self):
        i = self.PACKAGE.indicators[0]
        self.assertTrue(hasattr(i.title, "__datamarkings__"))
        self.assertEqual(len(i.title.__datamarkings__), 1)

        spec = next(iter(i.title.__datamarkings__))
        struct = spec.marking_structures[0]
        self.assertEqual(struct.color, "AMBER")

    def test_description_markings(self):
        i = self.PACKAGE.indicators[0]
        self.assertTrue(hasattr(i.description, "__datamarkings__"))
        self.assertEqual(len(i.description.__datamarkings__), 1)

        spec = next(iter(i.description.__datamarkings__))
        struct = spec.marking_structures[0]
        self.assertEqual(struct.color, "GREEN")


class ListXMLTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sio = StringIO(XML_LIST)
        cls.PARSER = parser.MarkingParser(sio)
        cls.PACKAGE = cls.PARSER.parse()

    def test_alternate_id_list(self):
        i = self.PACKAGE.indicators[0]
        foo = i.alternative_id[0]
        bar = i.alternative_id[1]

        self.assertTrue(hasattr(foo, "__datamarkings__"))
        self.assertTrue(hasattr(bar, "__datamarkings__"))

        fspec = next(iter(foo.__datamarkings__))
        bspec = next(iter(bar.__datamarkings__))

        self.assertTrue(fspec is bspec)
        self.assertEqual(fspec.marking_structures[0].color, "GREEN")
        self.assertEqual(bspec.marking_structures[0].color, "GREEN")


if __name__ == "__main__":
    unittest.main()
