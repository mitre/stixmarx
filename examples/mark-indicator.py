# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

from __future__ import print_function

# stixmarx imports
import stixmarx

# python-stix imports
from stix.indicator import Indicator
from stix.data_marking import MarkingSpecification
from stix.extensions.marking.tlp import TLPMarkingStructure as TLP


def main():
    # Create a new stixmarx MarkingContainer with a
    # new STIXPackage object contained within it.
    container = stixmarx.new()

    # Get the associated STIX Package
    package = container.package

    # Create an Indicator object
    indicator = Indicator(title='Indicator Title',
                          description='Gonna Mark This')

    # Add the Indicator object to our STIX Package
    package.add(indicator)

    # Build MarkingSpecification and add TLP MarkingStructure
    red_marking = MarkingSpecification(marking_structures=TLP(color="RED"))
    amber_marking = MarkingSpecification(marking_structures=TLP(color="AMBER"))
    green_marking = MarkingSpecification(marking_structures=TLP(color="GREEN"))

    # Mark the indicator with our TLP RED marking
    # This is the equivalent of a component marking. Applies to all descendants
    # nodes, text and attributes.
    container.add_marking(indicator, red_marking, descendants=True)

    # Mark the indicator with TLP GREEN. If descendants is false, the marking
    # will only apply to the indicator node. Does NOT include text, attributes
    # or descendants.
    container.add_marking(indicator, green_marking)

    # Mark the description text.
    # >>> type(indicator.description.value)  <type 'str'>
    indicator.description.value = container.add_marking(indicator.description.value, amber_marking)
    # >>> type(indicator.description.value)  <class 'stixmarx.api.types.MarkableBytes'>

    # Mark the indicator timestamp attribute.
    # >>> type(indicator.description.value)  <type 'datetime.datetime'>
    indicator.timestamp = container.add_marking(indicator.timestamp, amber_marking)
    # >>> type(indicator.description.value)  <type 'stixmarx.api.types.MarkableDateTime'>

    # Print the XML!
    print(container.to_xml().decode("utf-8"))


if __name__ == "__main__":
    main()
