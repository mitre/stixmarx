# Copyright (c) 2017, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

import pprint

# stixmarx
import stixmarx


def main():
    # Parse the input into a MarkingContainer
    container = stixmarx.parse("stix-document.xml")

    # Get container package
    package = container.package

    # Get the markings that apply to the entire XML document
    global_markings = container.get_markings(package)

    # Print the dictionary representation for our only global marking
    marking = global_markings[0]
    pprint.pprint(marking.to_dict())

    # Get our only indicator from the STIX Package
    indicator = package.indicators[0]

    # Get the markings from the Indicator.
    # Note: This will include the global markings and any other markings
    # applied by an ancestor!
    indicator_markings = container.get_markings(indicator)

    # Print the Indicator markings!
    for marking in indicator_markings:
        pprint.pprint(marking.to_dict())

if __name__ == "__main__":
    main()
