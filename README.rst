stixmarx
========

A Python API for marking STIX data.

:Source: https://github.com/mitre/stixmarx/
:Documentation: https://stixmarx.readthedocs.org/
:Information: https://stixproject.github.io/

|travis_badge| |landscape.io_badge| |version_badge|

Data Markings Concept
---------------------

Learn more about the Data Markings concept `here <https://stixproject.github.io/documentation/concepts/data-markings/>`_.

Examples
--------

The following examples demonstrate the intended use of the stixmarx library.

Adding Markings
~~~~~~~~~~~~~~~

.. code-block:: python

    # stixmarx imports
    import stixmarx

    # python-stix imports
    from stix.indicator import Indicator
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure as TLP


    # Create a new stixmarx MarkingContainer with a
    # new STIXPackage object contained within it.
    container = stixmarx.new()

    # Get the associated STIX Package
    package = container.package

    # Create an Indicator object
    indicator = Indicator(title='Indicator Title', description='Gonna Mark This')

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
    # >>> type(indicator.timestamp)  <type 'datetime.datetime'>
    indicator.timestamp = container.add_marking(indicator.timestamp, amber_marking)
    # >>> type(indicator.timestamp)  <type 'stixmarx.api.types.MarkableDateTime'>

    # Print the XML!
    print container.to_xml()

Retrieving Markings
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # stixmarx
    import stixmarx

    # Parse the input into a MarkingContainer
    container = stixmarx.parse("stix-document.xml")

    # Get container package
    package = container.package

    # Get the markings that apply to the entire XML document
    global_markings = container.get_markings(package)

    # Print the dictionary representation for our only global marking
    marking = global_markings[0]
    print marking.to_dict()

    # Get our only indicator from the STIX Package
    indicator = package.indicators[0]

    # Get the markings from the Indicator.
    # Note: This will include the global markings and any other markings
    # applied by an ancestor!
    indicator_markings = container.get_markings(indicator)

    # Print the Indicator markings!
    for marking in indicator_markings:
        print marking.to_dict()

Notice
------

This software was produced for the U. S. Government, and is subject to the
Rights in Data-General Clause 52.227-14, Alt. IV (DEC 2007).

Copyright (c) 2017, The MITRE Corporation. All Rights Reserved.

.. |travis_badge| image:: https://travis-ci.org/mitre/stixmarx.svg?branch=master&style=flat-square
    :target: https://travis-ci.org/mitre/stixmarx
    :alt: Travis CI Build Status
.. |landscape.io_badge| image:: https://landscape.io/github/mitre/stixmarx/master/landscape.svg?style=flat-square
    :target: https://landscape.io/github/mitre/stixmarx/master
    :alt: Landscape.io Code Health
.. |version_badge| image:: https://img.shields.io/pypi/v/stixmarx.svg?maxAge=3600&style=flat-square
    :target: https://pypi.python.org/pypi/stixmarx/
    :alt: PyPI Package Index
