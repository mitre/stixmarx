.. _overview:

Overview
========

``stixmarx`` is a Python library that allows the application of STIX data markings to python-stix, python-cybox and python-maec API objects. It is intended for use by Python software developers who want to incorporate field-level data marking capabilities into their STIX-processing software. For more about STIX data markings, see the `documentation on data markings <https://stixproject.github.io/documentation/concepts/data-markings/>`_ from the STIX project.

The library serves several broad functions:

 * Creating and managing markings on a STIX package
 * Parsing markings that are present in input XML

For a full set of examples with explanations, see the :ref:`examples` page. For the full ``MarkingContainer`` API, see the :ref:`api_reference`.

Be sure also to read the Usage Notes, below, for information on a few important non-obvious behaviors and usage requirements.

Applying Markings
-----------------

The STIX specification allows data markings to be applied to any combination of attributes and elements that can be described by XPath. Now, the ``stixmarx`` API can ease the process of apply markings by automating the process of generating XPath expressions during serialization. It provides support for global markings that is, markings the cover the entire STIX Package. Also, major STIX components (like Indicators, Incidents, etc.) and to CybOX Observables embedded in a STIX document. Finally, to specific attributes or text within the document.

Using the API to mark an element with the descendants option set to ``True`` also causes the marking to apply to all descendant elements and attributes under that marked element. For example, consider python-stix code to create an Incident with a related Indicator embedded inside of it:

.. testcode::

    container = stixmarx.new()
    package = container.package

    incident = Incident(title="An Incident")
    package.add_incident(incident)
     
    indicator = Indicator(idref="example:indicator-4273c681-487f-4e3b-0ef2-f36ebd0a6295")
    incident.related_indicators.append(indicator)
    
This corresponds to the XML result:

::

    <stix:Incident>
        <incident:Title>An Incident</incident:Title>
        <incident:Related_Indicators>
            <incident:Related_Indicator>
                <stixCommon:Indicator idref="example:indicator-4273c681-487f-4e3b-0ef2-f36ebd0a6295"/>
            </incident:Related_Indicator>
        </incident:Related_Indicators>
    </stix:Incident>

When using the ``stixmarx`` API to mark the outer Incident, the marking will also apply to all content inside the Incident, including the embedded ``<Title>``, ``<Related_Indicators>``, and ``<Indicator>`` elements.

.. testcode::

    marking_struct = TLPMarkingStructure(color='GREEN')
    marking_spec = MarkingSpecification()
    marking_spec.marking_structures.append(marking_struct)

    container.add_marking(incident, marking_spec, descendants=True)

This corresponds to the XML Result:

::

    <stix:Incident>
        <incident:Title>An Incident</incident:Title>
        <incident:Related_Indicators>
            <incident:Related_Indicator>
                <stixCommon:Indicator idref="example:indicator-4273c681-487f-4e3b-0ef2-f36ebd0a6295"/>
            </incident:Related_Indicator>
        </incident:Related_Indicators>
        <incident:Handling>
            <marking:Marking>
                <marking:Controlled_Structure>../../../descendant-or-self::node() | ../../../descendant-or-self::node()/@*</marking:Controlled_Structure>
                <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color="GREEN"/>
            </marking:Marking>
        </incident:Handling>
    </stix:Incident>

The central class for adding markings to a document is ``MarkingContainer``, which contains a ``python-stix`` STIXPackage object as its ``package`` property. The ``MarkingContainer`` class provides the ``add_marking``, ``get_markings``, and ``remove_marking`` functions for adding, retrieving, and removing markings on STIX, CybOX or MAEC components. It also supports the ``add_global`` and ``remove_global`` functions for adding and removing markings that apply to an entire document.

.. _parsing_overview:

Parsing Markings
----------------

When parsing XML into a python-stix data structure, stixmarx will attempt to capture any markings expressed in the XML and include them in the ``MarkingContainer``.

.. testcode::

    container = stixmarx.parse("stix_input.xml")
    package = container.package
    incident = package.incidents[0]
    print(container.get_markings(incident))
    >>> [<stix.data_marking.MarkingSpecification object at 0x...>, ...]

Now that the library can operate on major components and field-level markings, stixmarx's parsing capabilities are also extended to consume component markings, top-level collections (e.g., Indicators, TTPs, Observables) and field-level markings. Alternatively, package-level markings may apply to every element and attribute in the document (e.g., ``//node() | //@*``), to create a global marking.

Note that previous iterations of STIX Language documentation used ``//node()`` to select entire documents. This was found to be misaligned with the XPath 1.0 Specification and as such, the STIX Language documentation has been updated to reflect the proper selectors. This tool produces and consumes these selectors.

When encountering an unsupported or invalid XPath in a ``<Controlled_Structure>``, the parser will fail to apply the marking.

For more parsing examples with explanations, see the :ref:`examples` page.

Usage Notes
-----------

Below are several important notes about the design and usage of ``stixmarx``. Many of these points are addressed in examples on the :ref:`examples` page.

* When API functions say they accept a "marking" object, it means they accept a ``MarkingSpecification`` object, not a ``MarkingStructure``. If you have a ``MarkingStructure`` you wish to use to mark something, you must first place it inside a ``MarkingSpecification`` object and supply that object to the API.

* You can now use a single ``MarkingSpecification`` object multiple times. The API will create copies of the marking objects when it uses them during serialization (or flush). So it is now safe to apply markings using the same ``MarkingSpecification`` object for each call to ``add_marking`` and ``add_global``.

* ``MarkingSpecification`` objects supplied to ``add`` functions (``add_global``, ``add_marking``) should have an empty XPath ``controlled_structure`` value. The XPath will be populated by the library. The API user only needs to specify what object should be marked, and the API produces the appropriate XPath for that logical marking operation.

* Some python built-in types may be coerced into markable `stixmarx.api.types` when applying markings or parsing a document with markings that resolve or involve python built-in structures (e.g. str, datetime).

* ``add_marking(...)`` with descendants set to ``True`` marks an element and all descendant elements under it. It is the equivalent of a component marking in older versions of stixmarx. Correspondingly, ``get_markings(...)`` will return a list of all markings that apply directly to the given element `and` all inherited markings that have been applied to that element's ancestors.

* ``remove_marking(element, marking)`` can only remove markings that have been applied directly to the given element. Markings inherited from ancestor elements cannot be directly removed from a descendant element.
