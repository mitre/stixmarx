# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# stdlib
import unittest
from mixbox.vendor.six import StringIO

# external
from lxml import etree
from stix.indicator import Indicator
from stix.incident import Incident
from stix.data_marking import MarkingSpecification
from stix.extensions.marking.tlp import TLPMarkingStructure as TLP
from cybox.core import Observable
from cybox.objects.address_object import Address

# internal
import stixmarx
import stixmarx.errors as errors

STIX_XML_TEMPLATE_GLOBAL_AND_COMPONENT = """<stix:STIX_Package
    xmlns:cyboxCommon="http://cybox.mitre.org/common-2"
    xmlns:cybox="http://cybox.mitre.org/cybox-2"
    xmlns:cyboxVocabs="http://cybox.mitre.org/default_vocabularies-2"
    xmlns:marking="http://data-marking.mitre.org/Marking-1"
    xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
    xmlns:example="http://example.com"
    xmlns:indicator="http://stix.mitre.org/Indicator-2"
    xmlns:stixCommon="http://stix.mitre.org/common-1"
    xmlns:stixVocabs="http://stix.mitre.org/default_vocabularies-1"
    xmlns:stix="http://stix.mitre.org/stix-1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="
    http://cybox.mitre.org/common-2 http://cybox.mitre.org/XMLSchema/common/2.1/cybox_common.xsd
    http://cybox.mitre.org/cybox-2 http://cybox.mitre.org/XMLSchema/core/2.1/cybox_core.xsd
    http://cybox.mitre.org/default_vocabularies-2 http://cybox.mitre.org/XMLSchema/default_vocabularies/2.1/cybox_default_vocabularies.xsd
    http://data-marking.mitre.org/Marking-1 http://stix.mitre.org/XMLSchema/data_marking/1.1.1/data_marking.xsd
    http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1 http://stix.mitre.org/XMLSchema/extensions/marking/tlp/1.1.1/tlp_marking.xsd
    http://stix.mitre.org/Indicator-2 http://stix.mitre.org/XMLSchema/indicator/2.1.1/indicator.xsd
    http://stix.mitre.org/common-1 http://stix.mitre.org/XMLSchema/common/1.1.1/stix_common.xsd
    http://stix.mitre.org/default_vocabularies-1 http://stix.mitre.org/XMLSchema/default_vocabularies/1.1.1/stix_default_vocabularies.xsd
    http://stix.mitre.org/stix-1 http://stix.mitre.org/XMLSchema/core/1.1.1/stix_core.xsd" id="example:Package-88139233-3c7d-4913-bb5e-d2aeb079d029" version="1.1.1" timestamp="2015-02-26T21:00:37.453000+00:00">
    <stix:STIX_Header>
        <stix:Handling>
            <marking:Marking>
                <marking:Controlled_Structure>{0}</marking:Controlled_Structure>
                <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='AMBER'/>
            </marking:Marking>
        </stix:Handling>
    </stix:STIX_Header>
    <stix:Indicators>
        <stix:Indicator id="example:indicator-f0a233e2-6d21-4ea6-bf8c-ed4f57e10d31" timestamp="2015-04-04T12:24:08.458000Z" xsi:type='indicator:IndicatorType'>
            <indicator:Title>Test</indicator:Title>
            <indicator:Handling>
                <marking:Marking>
                    <marking:Controlled_Structure>{1}</marking:Controlled_Structure>
                    <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='RED'/>
                </marking:Marking>
            </indicator:Handling>
        </stix:Indicator>
    </stix:Indicators>
</stix:STIX_Package>
"""

STIX_XML_TEMPLATE_EMBEDDED_OBSERVABLE = """<stix:STIX_Package
    xmlns:cyboxCommon="http://cybox.mitre.org/common-2"
    xmlns:cybox="http://cybox.mitre.org/cybox-2"
    xmlns:cyboxVocabs="http://cybox.mitre.org/default_vocabularies-2"
    xmlns:AddressObj="http://cybox.mitre.org/objects#AddressObject-2"
    xmlns:marking="http://data-marking.mitre.org/Marking-1"
    xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
    xmlns:example="http://example.com"
    xmlns:indicator="http://stix.mitre.org/Indicator-2"
    xmlns:stixCommon="http://stix.mitre.org/common-1"
    xmlns:stixVocabs="http://stix.mitre.org/default_vocabularies-1"
    xmlns:stix="http://stix.mitre.org/stix-1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="
    http://cybox.mitre.org/common-2 http://cybox.mitre.org/XMLSchema/common/2.1/cybox_common.xsd
    http://cybox.mitre.org/cybox-2 http://cybox.mitre.org/XMLSchema/core/2.1/cybox_core.xsd
    http://cybox.mitre.org/default_vocabularies-2 http://cybox.mitre.org/XMLSchema/default_vocabularies/2.1/cybox_default_vocabularies.xsd
    http://cybox.mitre.org/objects#AddressObject-2 http://cybox.mitre.org/XMLSchema/objects/Address/2.1/Address_Object.xsd
    http://data-marking.mitre.org/Marking-1 http://stix.mitre.org/XMLSchema/data_marking/1.1.1/data_marking.xsd
    http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1 http://stix.mitre.org/XMLSchema/extensions/marking/tlp/1.1.1/tlp_marking.xsd
    http://stix.mitre.org/Indicator-2 http://stix.mitre.org/XMLSchema/indicator/2.1.1/indicator.xsd
    http://stix.mitre.org/common-1 http://stix.mitre.org/XMLSchema/common/1.1.1/stix_common.xsd
    http://stix.mitre.org/default_vocabularies-1 http://stix.mitre.org/XMLSchema/default_vocabularies/1.1.1/stix_default_vocabularies.xsd
    http://stix.mitre.org/stix-1 http://stix.mitre.org/XMLSchema/core/1.1.1/stix_core.xsd" id="example:Package-a63991ca-85d7-4b45-b3c5-d287e244c24f" version="1.1.1" timestamp="2015-03-05T16:19:54.603000+00:00">
    <stix:Indicators>
        <stix:Indicator id="example:indicator-44c5bff4-ecb7-4110-96af-27b1e964b815" timestamp="2013-04-04T12:24:08.458000Z" xsi:type='indicator:IndicatorType'>
            <indicator:Title>Test</indicator:Title>
            <indicator:Observable id="example:Observable-Target-ID-Value">
                <cybox:Object id="example:Address-70da2adc-5948-4fcf-a8bb-b9a91ab10f7a">
                    <cybox:Properties xsi:type="AddressObj:AddressObjectType">
                        <AddressObj:Address_Value>10.0.0.1</AddressObj:Address_Value>
                    </cybox:Properties>
                </cybox:Object>
            </indicator:Observable>
            <indicator:Handling>
                <marking:Marking>
                    <marking:Controlled_Structure>{0}</marking:Controlled_Structure>
                    <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='RED'/>
                </marking:Marking>
                <marking:Marking>
                    <marking:Controlled_Structure>{1}</marking:Controlled_Structure>
                    <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='AMBER'/>
                </marking:Marking>
            </indicator:Handling>
        </stix:Indicator>
    </stix:Indicators>
</stix:STIX_Package>
"""


class MarkingTest(unittest.TestCase):

    def test_component_marking(self):
        """Test that top-level STIX components are marked correctly"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        
        indicator = Indicator(title="Test")
        package.add_indicator(indicator)
        
        container.add_marking(indicator, red_marking, descendants=True)
        
        self.assertTrue(container.is_marked(indicator, red_marking))

    def test_global_package_marking(self):
        """Test that global markings apply to the package and TLOs"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        container.add_global(red_marking)
        
        indicator = Indicator(title="Test")
        package.add_indicator(indicator)
        
        self.assertTrue(container.is_marked(indicator, red_marking))
        self.assertTrue(container.is_marked(package, red_marking))
        
    def test_global_marking_on_observables(self):
        """Test that global markings apply to Obseravbles"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        container.add_global(red_marking)
        
        observable = generate_observable()
        package.add_observable(observable)
        
        self.assertTrue(container.is_marked(observable, red_marking))
        self.assertFalse(container.is_marked(observable, MarkingSpecification()))

    def test_package_marking_error(self):
        """Marking a package with `add(package, marking)` is not allowed. Use `add_global(marking)` instead."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())

        self.assertRaises(errors.UnmarkableError, container.add_marking, package, red_marking)
        
    def test_observable_marking(self):
        """Test that Observables can be marked directly"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        
        observable = generate_observable()
        package.add_observable(observable)
        container.add_marking(observable, red_marking)
        
        self.assertTrue(container.is_marked(observable, red_marking))

    def test_embedded_component_marking(self):
        """Test that embedded STIX components are marked according to their parent TLO and global markings"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        amber_marking = generate_marking_spec(generate_amber_marking_struct())
        
        incident = Incident(title="Test")
        package.add_incident(incident)
        
        indicator = Indicator(title="Test")
        incident.related_indicators.append(indicator)
        
        container.add_marking(incident, red_marking, descendants=True)
        container.add_global(amber_marking)
        
        self.assertTrue(container.is_marked(indicator, red_marking))
        self.assertTrue(container.is_marked(indicator, amber_marking))

    def test_marking_duplication(self):
        """Test that embedded STIX components are marked according to their parent TLO and global markings"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        amber_marking = generate_marking_spec(generate_amber_marking_struct())

        incident = Incident(title="Test")
        package.add_incident(incident)

        indicator = Indicator(title="Test")
        incident.related_indicators.append(indicator)

        container.add_marking(incident, red_marking, descendants=True)
        container.add_global(amber_marking)

        self.assertTrue(container.is_marked(indicator, red_marking))
        self.assertTrue(container.is_marked(indicator, amber_marking))

        markings = container.get_markings(indicator)
        self.assertEqual(len(markings), 2)
        
    def test_embedded_component_direct_marking(self):
        """Test that embedded STIX components can be directly marked"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        
        incident = Incident(title="Test")
        package.add_incident(incident)
        
        indicator = Indicator(title="Test")
        incident.related_indicators.append(indicator)
        
        container.add_marking(indicator, red_marking)
        
        self.assertTrue(container.is_marked(indicator, red_marking))
        
    def test_embedded_observable_marking(self):
        """Test that embedded Observables are marked according to their parent TLO and global markings"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        amber_marking = generate_marking_spec(generate_amber_marking_struct())
        
        indicator = Indicator(title="Test")
        package.add_indicator(indicator)
        
        observable = generate_observable()
        indicator.add_observable(observable)
        
        container.add_marking(indicator, red_marking, descendants=True)
        container.add_global(amber_marking)
        
        self.assertTrue(container.is_marked(observable, red_marking))
        self.assertTrue(container.is_marked(observable, amber_marking))
        
    def test_embedded_observable_direct_marking(self):
        """Test that embedded Observables can be directly marked"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        amber_marking = generate_marking_spec(generate_amber_marking_struct())
        
        indicator = Indicator(title="Test")
        package.add_indicator(indicator)
        
        observable = generate_observable()
        indicator.add_observable(observable)
        
        container.add_marking(indicator, amber_marking)
        container.add_marking(observable, red_marking)
        
        self.assertTrue(container.is_marked(observable, red_marking))

    def test_marking_path_parsing(self):
        """Test that parsed paths are applied correctly"""
        
        # paths to attempt for a global AMBER marking
        global_xpaths = [
            {
                "path": "//node() | //@*",
                "should_pass": True
            },
            {
                "path": "this is not a real xpath",
                "should_pass": False
            }
        ]
        # paths to attempt for a local RED marking
        local_xpaths = [
            {
                "path": "../../../descendant-or-self::node() | ../../../descendant-or-self::node()/@*",
                "should_pass": True
            },
            {
                "path": "this is not a real xpath",
                "should_pass": False
            }
        ]

        for global_path_dict in global_xpaths:
            for local_path_dict in local_xpaths:
                # Format our STIX XML template
                xml = STIX_XML_TEMPLATE_GLOBAL_AND_COMPONENT.format(global_path_dict["path"], local_path_dict["path"])
                xml_readable = StringIO(xml)

                # Build and parse the MarkingContainer
                try:
                    container = stixmarx.parse(xml_readable)
                except etree.XPathEvalError:
                    self.assertTrue(global_path_dict["should_pass"] is False or local_path_dict["should_pass"] is False)
                    continue

                package = container.package

                colors = [marking_spec.marking_structures[0].color for marking_spec in container.get_markings(package.indicators[0])]

                self.assertTrue(('AMBER' in colors) == global_path_dict["should_pass"])
                self.assertTrue(('RED' in colors) == local_path_dict["should_pass"])

    def test_marking_path_parsing_for_observable(self):
        """Test that parsed paths are applied correctly to Observable"""
        
        # paths to attempt for a component RED marking
        observable_xpaths = [
            {
                "path": "../../../indicator:Observable[1]/descendant-or-self::node() | ../../../indicator:Observable[1]/descendant-or-self::node()/@*",
                "should_pass": True
            },
            {
                "path": "this is not a real xpath",
                "should_pass": False
            }
        ]
        # paths to attempt for a component AMBER marking
        component_xpaths = [
            {
                "path": "../../../descendant-or-self::node() | ../../../descendant-or-self::node()/@*",
                "should_pass": True
            },
            {
                "path": "this is not a real xpath",
                "should_pass": False
            }
        ]

        for observable_path_dict in observable_xpaths:
            for component_path_dict in component_xpaths:
                # Format our STIX XML template
                xml = STIX_XML_TEMPLATE_EMBEDDED_OBSERVABLE.format(
                    observable_path_dict["path"],
                    component_path_dict["path"]
                )
                xml_readable = StringIO(xml)

                # Build and parse the MarkingContainer
                try:
                    container = stixmarx.parse(xml_readable)
                except etree.XPathEvalError:
                    self.assertTrue(observable_path_dict["should_pass"] is False or component_path_dict["should_pass"] is False)
                    continue

                package = container.package

                colors = [marking_spec.marking_structures[0].color for marking_spec in container.get_markings(package.indicators[0].observable)]

                self.assertTrue(('RED' in colors) == observable_path_dict["should_pass"])
                self.assertTrue(('AMBER' in colors) == component_path_dict["should_pass"])
    
    def test_marking_removal(self):
        """Test that markings can be removed"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        
        indicator = Indicator(title="Test")
        package.add_indicator(indicator)
        
        container.add_marking(indicator, red_marking)
        self.assertTrue(container.is_marked(indicator, red_marking))

        container.remove_marking(indicator, red_marking)
        self.assertFalse(container.is_marked(indicator, red_marking))
        
    def test_embedded_marking_removal(self):
        """Test that markings can be removed"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        
        incident = Incident(title="Test")
        package.add_incident(incident)
        
        indicator = Indicator(title="Test")
        incident.related_indicators.append(indicator)
        
        container.add_marking(indicator, red_marking)
        self.assertTrue(container.is_marked(indicator, red_marking))

        container.remove_marking(indicator, red_marking)
        self.assertFalse(container.is_marked(indicator, red_marking))
        
    def test_observable_marking_removal(self):
        """Test that Observables can be marked directly"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        
        observable = generate_observable()
        package.add_observable(observable)
        
        container.add_marking(observable, red_marking)

        self.assertTrue(container.is_marked(observable, red_marking))
        container.remove_marking(observable, red_marking)
        self.assertFalse(container.is_marked(observable, red_marking))
        
    def test_embedded_observable_marking_removal(self):
        """Test that markings on embedded Observables can be removed"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        
        indicator = Indicator(title="Test")
        package.add_indicator(indicator)
        
        observable = generate_observable()
        indicator.add_observable(observable)
        
        container.add_marking(observable, red_marking)
        self.assertTrue(container.is_marked(observable, red_marking))

        container.remove_marking(observable, red_marking)
        self.assertFalse(container.is_marked(observable, red_marking))
        
    def test_remove_parent_marking_failure(self):
        """Test that inherited parent markings cannot be removed from children"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
          
        incident = Incident(title="Test")
        package.add_incident(incident)
        
        indicator = Indicator(title="Test")
        incident.related_indicators.append(indicator)
        
        container.add_marking(incident, red_marking, descendants=True)
        self.assertTrue(container.is_marked(incident, red_marking))
        self.assertTrue(container.is_marked(indicator, red_marking))
        self.assertRaises(errors.MarkingRemovalError, container.remove_marking, indicator, red_marking, True)
        
    def test_remove_parent_marking_for_observable_failure(self):
        """Test that inherited parent markings cannot be removed from children"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        
        indicator = Indicator(title="Test")
        package.add_indicator(indicator)
        
        observable = generate_observable()
        indicator.add_observable(observable)
        
        container.add_marking(indicator, red_marking, descendants=True)

        self.assertTrue(container.is_marked(observable, red_marking))
        self.assertTrue(container.is_marked(indicator, red_marking))
        self.assertRaises(errors.MarkingRemovalError, container.remove_marking, observable, red_marking)

    def test_absent_marking_removal_failure(self):
        """Test that markings can be removed"""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        
        indicator = Indicator(title="Test")
        package.add_indicator(indicator)
        self.assertRaises(errors.MarkingNotFoundError, container.remove_marking, indicator, red_marking)
        
        observable = generate_observable()
        package.add_observable(observable)
        self.assertRaises(errors.MarkingNotFoundError, container.remove_marking, observable, red_marking)

    def test_duplicate_check(self):
        container = stixmarx.new()
        package = container.package
        indicator = Indicator(title="Test")
        package.add(indicator)

        red_marking = generate_marking_spec(generate_red_marking_struct())
        container.add_marking(indicator, red_marking)

        # Test that our marking has been added
        self.assertTrue(container.is_marked(indicator, red_marking))
        self.assertTrue(red_marking in container.get_markings(indicator))

        # Test that the trying to re-add the original would raise an error
        self.assertRaises(
            errors.DuplicateMarkingError,
            container.add_marking,
            indicator,
            red_marking
        )

    def test_is_marked(self):
        container = stixmarx.new()
        package = container.package
        indicator = Indicator(title="Test")
        package.add(indicator)

        red_struct = generate_red_marking_struct()
        red_marking = generate_marking_spec(red_struct)
        container.add_marking(indicator, red_marking)

        # Test that our marking has been added
        self.assertTrue(container.is_marked(indicator, red_marking))

    def test_remove_null_making(self):
        container = stixmarx.new()

        red_struct = generate_red_marking_struct()
        red_marking = generate_marking_spec(red_struct)
        container.add_marking(None, red_marking)

        self.assertTrue(len(container.null_markings) == 1)

        container.remove_marking(None, red_marking)

        self.assertTrue(len(container.null_markings) == 0)


def generate_red_marking_struct():
    return TLP(color='RED')


def generate_amber_marking_struct():
    return TLP(color='AMBER')


def generate_marking_spec(struct):
    spec = MarkingSpecification()
    spec.marking_structures.append(struct)
    return spec


def generate_observable(cybox_obj=None):
    cybox_obj = cybox_obj or Address(address_value='10.0.0.1')
    return Observable(cybox_obj)


if __name__ == "__main__":
    unittest.main()
