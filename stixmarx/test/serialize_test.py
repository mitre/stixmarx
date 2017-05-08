# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

from __future__ import print_function

# stdlib
import unittest
from mixbox.vendor.six import StringIO

# external
from cybox.core import Observable
from cybox.objects.address_object import Address
from stix.common.kill_chains import KillChain, KillChainPhase
from stix.core import ttps
from stix.data_marking import MarkingSpecification
from stix.extensions.marking.tlp import TLPMarkingStructure as TLP
from stix.incident import Incident
from stix.indicator import Indicator

# internal
import stixmarx
from stixmarx import api
from stixmarx import errors
from stixmarx import navigator
from stixmarx import xml


class SerializeTest(unittest.TestCase):

    def test_marking_flush(self):
        """Tests that markings do not affect a package until flushed from
            the container."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        amber_marking = generate_marking_spec(generate_amber_marking_struct())

        indicator = Indicator(title="Test")
        package.add_indicator(indicator)
        container.add_marking(indicator, amber_marking)
        container.add_global(red_marking)

        # package has not been changed yet
        self.assertTrue(package.indicators[0].handling is None)
        self.assertTrue(package.stix_header is None or
                        package.stix_header.handling is None)

        container.flush()

        # package has been changed by markings
        self.assertTrue(package.indicators[0].handling.marking[0] is not None)
        self.assertTrue(package.stix_header.handling.marking[0] is not None)

    def test_marking_round_trip(self):
        """Test that get_markings() yields the same number of results after
            calling to_xml()."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())
        amber_marking = generate_marking_spec(generate_amber_marking_struct())

        incident = Incident(title="Test Incident")
        package.add_incident(incident)

        indicator = Indicator(idref="example:Indicator-test-1234")
        incident.related_indicators.append(indicator)

        container.add_marking(incident, red_marking, descendants=True)
        container.add_global(amber_marking)

        self.assertTrue(container.is_marked(indicator, red_marking))
        self.assertTrue(container.is_marked(indicator, amber_marking))

        markings = container.get_markings(indicator)
        self.assertEqual(len(markings), 2)

        xml = container.to_xml()

        sio = StringIO(xml.decode("utf-8"))
        new_xml_container = stixmarx.parse(sio)

        parsed_indicator = new_xml_container.package.incidents[0].related_indicators[0]
        parsed_markings = new_xml_container.get_markings(parsed_indicator)

        for x in parsed_markings:
            print(x.to_dict())

        self.assertEqual(len(parsed_markings), 2)

    def test_local_marking_placement(self):
        """Test that marking an individual field whose parent or self object
            contains a handling structure is placed correctly."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())

        indicator = Indicator(title="Test")
        # STIX 1.1.1 doesn't have multiple descriptions
        indicator.description = "Test description"

        package.add_indicator(indicator)

        container.add_marking(indicator.description, red_marking)

        self.assertTrue(package.indicators[0].handling is None)
        self.assertTrue(package.stix_header is None)

        container.flush()

        self.assertTrue(package.stix_header is None)
        self.assertTrue(
                package.indicators[0].handling.marking[0].controlled_structure
                is not None)

    def test_stix_header_marking_placement(self):
        """Test that marking an individual field whose parent does not contain
            a handling structure, marking is placed in stix header."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())

        kill_chain = KillChain(id_="example:kc-1234", name="Test Kill Chain")
        kill_chain_phase = KillChainPhase(phase_id="example:kcp-1234",
                                          name="Test Kill Chain Phase")

        test_ttps = ttps.TTPs()
        package.ttps = test_ttps

        kill_chain.add_kill_chain_phase(kill_chain_phase)
        package.ttps.kill_chains.kill_chain.append(kill_chain)

        container.add_marking(kill_chain_phase, red_marking)

        self.assertTrue(package.stix_header is None)

        container.flush()

        self.assertTrue(
                package.stix_header.handling.marking[0].controlled_structure
                is not None)

    def test_global_marking_placement(self):
        """Test that global markings are placed in stix header."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())

        container.add_global(red_marking)

        self.assertTrue(package.stix_header is None)

        container.flush()

        self.assertTrue(
                package.stix_header.handling.marking[0].controlled_structure
                is not None)

    def test_markable_text_nodes(self):
        """Test that text selector is used on resulting xpath.
            Does not check for accuracy of marked data."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())

        indicator = Indicator(title="Test")
        # STIX 1.1.1 doesn't have multiple descriptions
        indicator.description = "Test description"
        observable = generate_observable()
        indicator.add_observable(observable)

        package.add_indicator(indicator)

        observable.object_.properties.address_value.value = \
            container.add_marking(
                    observable.object_.properties.address_value.value,
                    red_marking
            )

        indicator.description.value = \
            container.add_marking(
                    indicator.description.value,
                    red_marking
            )

        self.assertTrue(package.stix_header is None)
        self.assertTrue(package.indicators[0].handling is None)

        container.flush()

        self.assertTrue(package.stix_header is None)
        self.assertTrue(package.indicators[0].handling is not None)

        for marking in package.indicators[0].handling.marking:
            selector = marking.controlled_structure.split("/")[-1]

            self.assertTrue("text()" == selector)

        print(package.to_xml().decode("utf-8"))

    def test_markable_attributes(self):
        """Test that attribute selector used on resulting xpath.
            Does not check for accuracy of marked data."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())

        indicator = Indicator(title="Test")
        observable = generate_observable()

        indicator.add_observable(observable)

        package.add_indicator(indicator)

        observable.object_.id_ = container.add_marking(observable.object_.id_, red_marking)
        indicator.timestamp = container.add_marking(indicator.timestamp, red_marking)

        self.assertTrue(package.stix_header is None)
        self.assertTrue(package.indicators[0].handling is None)

        container.flush()

        self.assertTrue(package.stix_header is None)

        self.assertTrue(package.indicators[0].handling is not None)

        for marking in package.indicators[0].handling.marking:
            selector = marking.controlled_structure.split("/")[-1]

            self.assertTrue(selector.startswith("@"))

    def test_duplicate_marking(self):
        """Test that duplicate markings get added once."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())

        indicator = Indicator(title="Test")

        package.add_indicator(indicator)

        container.add_marking(indicator, red_marking)
        self.assertRaises(errors.DuplicateMarkingError, container.add_marking, indicator, red_marking, False)

        container.add_global(red_marking)
        self.assertRaises(errors.DuplicateMarkingError, container.add_global, red_marking)

        self.assertTrue(indicator.handling is None)
        self.assertTrue(package.stix_header is None)

        container.flush()

        self.assertTrue(len(indicator.handling.marking) == 1)
        self.assertTrue(len(package.stix_header.handling.marking) == 1)

    def test_markable_self_node(self):
        """Test that a marking to an element with descendants=False will result
        in ``self::node()`` selector."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())

        indicator = Indicator(title="Test")

        package.add_indicator(indicator)

        container.add_marking(indicator, red_marking)

        self.assertTrue(package.indicators[0].handling is None)

        container.flush()

        indicator_path = package.indicators[0].handling.marking[0] \
            .controlled_structure.split("/")[-1]

        self.assertTrue(indicator_path == xml.XPATH_AXIS_SELF_NODE)

        counter = 0
        for elem in navigator.iterwalk(package):
            if api.is_marked(elem):
                counter += 1

        # There should be only one object with markings in the whole package.
        self.assertTrue(counter == 1)

    def test_null_marking_serialization(self):
        """Test that a null marking gets serialized."""
        container = stixmarx.new()
        package = container.package
        red_marking = generate_marking_spec(generate_red_marking_struct())

        indicator = Indicator(title="Test")

        package.add_indicator(indicator)

        container.add_marking(None, red_marking)

        self.assertTrue(package.stix_header is None or
                        package.stix_header.handling is None)

        container.flush()

        self.assertTrue(package.stix_header.handling is not None)


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
