.. _examples:

Examples
________

The following examples will provide developers initial background on how to use the stixmarx API.

Managing Markings
=================

Creating a Container
--------------------

To apply any markings, we first need to create a ``MarkingContainer``. The ``stixmarx.new()`` function creates a new container, with an empty STIX Package inside.

.. testcode::

   import stixmarx

   container = stixmarx.new()
   stix_package = container.package
   
You can also create a container with a non-empty package by supplying an XML filepath to ``stixmarx.parse(...)``:

.. testcode::

   import stixmarx

   container = stixmarx.parse("stix_input.xml")
   stix_package = container.package
   
Or supply a ``read``-able IO object:
   
.. testcode::
   
   import stixmarx
   from mixbox.vendor.six import StringIO

   xml_string = "<stix:STIX_Package>..."
   xml_readable = StringIO(xml_string)

   container = stixmarx.parse(xml_readable)
   stix_package = container.package
   
When parsing the XML input, the library will attempt to apply any markings found in ``<Handling>`` sections. This behavior is limited to markings defined by XPaths that the library can handle; see `Parsing Markings`_ for more information.

Applying Markings
-----------------

STIX Components can be marked by ``MarkingContainer::add_marking``. The ``add_marking`` function accepts a STIX, CybOX and MAEC entity, a ``MarkingSpecification`` object and a optional ``True`` or ``False`` value to signal the container the marking applies only to the entity or to the entity and all descendants.

The following example resembles the regular component marking.

.. testcode::

    import stixmarx
    from stix.indicator import Indicator
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure

    container = stixmarx.new()
    stix_package = container.package

    indicator = Indicator(title="Test")
    stix_package.add_indicator(indicator)

    marking_struct = TLPMarkingStructure(color='RED')
    marking_spec = MarkingSpecification()
    marking_spec.marking_structures.append(marking_struct)

    container.add_marking(indicator, marking_spec, descendants=True)
   
Note that marking functions accept a ``MarkingSpecification`` object, not a ``MarkingStructure`` object. A ``MarkingSpecification`` object contains ``MarkingStructure`` objects (per the ``marking_spec.marking_structures.append(marking_struct)`` line). The marking object's ``controlled_structure`` property should not be set. The API will set it for you, based on how you use the API to apply the marking.
   
Markings can be applied to an entire document with ``add_global``:
   
.. testcode::

    import stixmarx
    from stix.indicator import Indicator
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure

    container = stixmarx.new()
    stix_package = container.package

    indicator = Indicator(title="Test")
    stix_package.add_indicator(indicator)

    marking_struct = TLPMarkingStructure(color='RED')
    marking_spec = MarkingSpecification()
    marking_spec.marking_structures.append(marking_struct)

    container.add_global(marking_spec)
   
Note that you cannot mark a STIX Package object with ``add_marking``. Instead, you must use ``add_global``.

User's may also apply markings to specific attributes or text from the document.

.. testcode::

    import stixmarx
    from stix.indicator import Indicator
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure

    container = stixmarx.new()
    stix_package = container.package

    indicator = Indicator(title="Test")
    indicator.description = "A test description"
    stix_package.add_indicator(indicator)

    marking_struct = TLPMarkingStructure(color='RED')
    marking_spec = MarkingSpecification()
    marking_spec.marking_structures.append(marking_struct)

    indicator.description.value = container.add_marking(indicator.description.value, marking_spec)

Note: When markings to attribute or text are applied, the descendants option is ignored. Also, if the values to mark are Python built-in types, they will be coerced into ``stixmarx.api.types`` objects according to the following table:

=============================   =============================
Python built-in type            stixmarx.api.types
=============================   =============================
bool                            MarkableBool
int                             MarkableInt
long (only in Python 2)         MarkableLong
float                           MarkableFloat
six.binary_type                 MarkableBytes
six.text_type                   MarkableText
datetime.date                   MarkableDate
datetime.datetime               MarkableDateTime
=============================   =============================

Attribute example,

.. testcode::

   import stixmarx
   from stix.indicator import Indicator
   from stix.data_marking import MarkingSpecification
   from stix.extensions.marking.tlp import TLPMarkingStructure

   container = stixmarx.new()
   stix_package = container.package

   indicator = Indicator(title="Test")
   stix_package.add_indicator(indicator)

   marking_struct = TLPMarkingStructure(color='RED')
   marking_spec = MarkingSpecification()
   marking_spec.marking_structures.append(marking_struct)

   indicator.timestamp = container.add_marking(indicator.timestamp, marking_spec)

Marking only the node example,

.. testcode::

    import stixmarx
    from stix.indicator import Indicator
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure

    container = stixmarx.new()
    stix_package = container.package

    indicator = Indicator(title="Test")
    stix_package.add_indicator(indicator)

    marking_struct = TLPMarkingStructure(color='RED')
    marking_spec = MarkingSpecification()
    marking_spec.marking_structures.append(marking_struct)

    container.add_marking(indicator.title, marking_spec)

Reading Markings
----------------

The ``MarkingContainer::get_markings`` function returns a list of markings that apply to an element.

.. testcode::

    import stixmarx
    from stix.indicator import Indicator
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure

    container = stixmarx.new()
    stix_package = container.package
    indicator = Indicator(title="Test")
    stix_package.add_indicator(indicator)

    marking_spec = MarkingSpecification(marking_structures=TLPMarkingStructure(color='RED'))
    container.add_marking(indicator, marking_spec)

    print container.get_markings(indicator)
   
Since markings are applied recursively to descendants, any descendant elements nested inside of a marked element also report the ancestor's markings.

.. testcode::

    import stixmarx
    from stix.indicator import Indicator
    from stix.incident import Incident
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure

    container = stixmarx.new()
    package = container.package

    incident = Incident(title="My incident")
    package.add_incident(incident)
    indicator = Indicator(title="Sample indicator")
    incident.related_indicators.append(indicator)

    green_marking_spec = MarkingSpecification(marking_structures=TLPMarkingStructure(color='GREEN'))
    container.add_global(green_marking_spec)

    amber_marking_spec = MarkingSpecification(marking_structures=TLPMarkingStructure(color='AMBER'))
    container.add_marking(incident, amber_marking_spec, descendants=True)

    red_marking_spec = MarkingSpecification(marking_structures=TLPMarkingStructure(color='RED'))
    container.add_marking(indicator, red_marking_spec, descendants=True)

    print container.get_markings(incident)
    print container.get_markings(indicator)
   
This will show a list of two ``MarkingSpecification`` objects applied to the Incident: global GREEN and local AMBER. It will show three markings on the nested Indicator: global GREEN, parent AMBER, and local RED.

Global markings for a container are stored in the ``MarkingContainer::global_markings`` list. While component and field markings are stored in ``MarkingContainer::field_markings``.

Removing Markings
-----------------

To remove a marking, use ``MarkingContainer::remove_marking``.

.. testcode::

    import stixmarx
    from stix.indicator import Indicator
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure

    container = stixmarx.new()
    package = container.package

    indicator = Indicator(title="Test")
    package.add_indicator(indicator)

    marking_spec = MarkingSpecification(marking_structures=TLPMarkingStructure(color='RED'))

    container.add_marking(indicator, marking_spec, descendants=True)
    print container.get_markings(indicator)

    container.remove_marking(indicator, marking_spec, descendants=True)
    print container.get_markings(indicator)

A marking can only be removed from an element if that marking was originally applied directly to that element. That means, you cannot remove a marking inherited from an ancestor. The rule applies for both situations: generating or parsing existing content.

.. testcode::

    import stixmarx
    from stix.indicator import Indicator
    from stix.incident import Incident
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure

    container = stixmarx.new()
    package = container.package

    marking_spec = MarkingSpecification(marking_structures=TLPMarkingStructure(color='RED'))

    incident = Incident(title="Test Incident")
    package.add_incident(incident)

    indicator = Indicator()
    incident.related_indicators.append(indicator)

    container.add_marking(incident, marking_spec, descendants=True)

    # show marking, inherited from incident
    print container.get_markings(indicator)

    # ERROR: indicator was never marked; it inherits a marking from incident
    container.remove_marking(indicator, marking_spec)

Also, when generating content, the same marking and descendants option MUST be supplied to ``MarkingContainer::remove_marking`` in order to properly remove the marking.

Global markings can be removed via the ``MarkingContainer::remove_global`` method.

.. testcode::

    import stixmarx
    from stix.indicator import Indicator
    from stix.incident import Incident
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure

    container = stixmarx.new()
    package = container.package

    marking_spec = MarkingSpecification(marking_structures=TLPMarkingStructure(color='RED'))

    incident = Incident(title="Test Incident")
    package.add_incident(incident)

    indicator = Indicator()
    incident.related_indicators.append(indicator)

    container.add_global(marking_spec)

    # show marking, inherited from global
    print container.get_markings(indicator)

    container.remove_global(marking_spec)

Observable Markings
-------------------

Observables can be marked in the same way that STIX components are marked.

.. testcode::

    import stixmarx
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure
    from cybox.core import Observable
    from cybox.objects.address_object import Address

    container = stixmarx.new()
    package = container.package

    red_marking = MarkingSpecification(marking_structures=TLPMarkingStructure(color='RED'))

    observable = Observable(Address(address_value='10.0.0.1'))
    package.add_observable(observable)

    container.add_marking(observable, red_marking, descendants=True)

    print container.get_markings(observable)

However, because observables cannot contain their own ``Marking`` element, and must be marked externally, stixmarx will store the resulting ``Marking`` under the STIX_Header of the document when there is no available ancestor with a ``Handling`` element. Note: ``id`` attributes are no longer used for XPath generation since they are optional.

Top Collections Markings
------------------------

The stixmarx API is now capable of marking Top Collections, for example: (TTPs, Indicators, Observables). Top Collections can be marked the same way as any other STIX component.

.. testcode::

    import stixmarx
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure
    from cybox.core import Observable
    from cybox.objects.address_object import Address

    container = stixmarx.new()
    package = container.package

    red_marking = MarkingSpecification(marking_structures=TLPMarkingStructure(color='RED'))

    observable = Observable(Address(address_value='10.0.0.1'))
    package.add_observable(observable)

    container.add_marking(package.observables, red_marking, descendants=True)

    print container.get_markings(observable)

Output Markings
---------------

To output an XML document string with markings included, use ``MarkingContainer::to_xml``:

.. testcode::

    import stixmarx
    from stix.data_marking import MarkingSpecification
    from stix.extensions.marking.tlp import TLPMarkingStructure

    container = stixmarx.parse("input_package.xml")

    marking_spec = MarkingSpecification(marking_structures=TLPMarkingStructure(color='RED'))

    container.add_global(marking_spec)
    print container.to_xml()
   
``MarkingContainer::to_xml`` takes the exact same arguments as python-stix's ``Entity::to_xml``.

Parsing Markings
================

These examples demonstrate how to write XML that can be parsed into marking data structures by stixmarx. See the :ref:`parsing_overview` section from the :ref:`overview` page for more information.

Parsing STIX Components
-----------------------

To mark an element from its ``<Handling>`` section, the XPath ``../../../descendant-or-self::node() | ../../../descendant-or-self::node()/@*`` is appropriate. This XPath should go in a ``<Controlled_Structure>``, inside a ``<Marking>``, inside the element being marked, like an ``<Indicator>``.

Suppose we have a this content in ``doc.xml``, where a RED TLP marking has been applied to an Indicator:

.. testcode::

    <stix:STIX_Package
        xmlns:example="http://example.com"
        xmlns:indicator="http://stix.mitre.org/Indicator-2"
        xmlns:marking="http://data-marking.mitre.org/Marking-1"
        xmlns:stix="http://stix.mitre.org/stix-1"
        xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="example:Package-5c5ecffe-9025-42ac-83ea-a3b7158bea1a" version="1.2">
        <stix:Indicators>
            <stix:Indicator id="example:indicator-64d3d246-487e-4003-9366-90aa2b49570c" timestamp="2016-03-30T15:58:30.662000Z" xsi:type='indicator:IndicatorType'>
                <indicator:Title>Test Title</indicator:Title>
                <indicator:Handling>
                    <marking:Marking>
                        <marking:Controlled_Structure>../../../descendant-or-self::node() | ../../../descendant-or-self::node()/@*</marking:Controlled_Structure>
                        <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='RED'/>
                    </marking:Marking>
                </indicator:Handling>
            </stix:Indicator>
        </stix:Indicators>
    </stix:STIX_Package>

Then we can parse the ``doc.xml`` document and inspect the marking like so:

.. testcode::

    import stixmarx

    container = stixmarx.parse("doc.xml")
    stix_package = container.package

    indicator = stix_package.indicators[0]
    print container.get_markings(indicator)
   
Parsing Global Markings
-----------------------

Markings in the the ``<Handling>`` section of the ``<STIX_Header>`` may apply to every element and attribute in the document (e.g., ``//node | //@*``). This corresponds to a global marking in the API. Now, MarkingContainer does not return global markings from it's global_markings. User's can check the STIX Package for markings.

.. testcode::

    <stix:STIX_Package
        xmlns:example="http://example.com"
        xmlns:indicator="http://stix.mitre.org/Indicator-2"
        xmlns:marking="http://data-marking.mitre.org/Marking-1"
        xmlns:stix="http://stix.mitre.org/stix-1"
        xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="example:Package-3972115d-3e88-4688-8dff-6208bcf1db55" version="1.2">
        <stix:STIX_Header>
            <stix:Handling>
                <marking:Marking>
                    <marking:Controlled_Structure>//node() | //@*</marking:Controlled_Structure>
                    <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='RED'/>
                </marking:Marking>
            </stix:Handling>
        </stix:STIX_Header>
        <stix:Indicators>
            <stix:Indicator id="example:indicator-08174fbc-115f-46d6-890b-4214fbd8c3e4" timestamp="2016-03-30T15:58:30.662000Z" xsi:type='indicator:IndicatorType'>
                <indicator:Title>Test</indicator:Title>
            </stix:Indicator>
        </stix:Indicators>
    </stix:STIX_Package>

We can parse the document (named, e.g., ``doc.xml``) and read the global marking like so:

.. testcode::

    import stixmarx

    container = stixmarx.parse("doc.xml")
    package = container.package

    print container.get_markings(package)

Note: The example above will only return globally applied markings. Now, if a user desires to capture all markings present in the document regardless of the scope (global, component or field) see example below.

.. testcode::

    <stix:STIX_Package
        xmlns:example="http://example.com"
        xmlns:indicator="http://stix.mitre.org/Indicator-2"
        xmlns:marking="http://data-marking.mitre.org/Marking-1"
        xmlns:stix="http://stix.mitre.org/stix-1"
        xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="example:Package-3972115d-3e88-4688-8dff-6208bcf1db55" version="1.2">
        <stix:STIX_Header>
            <stix:Handling>
                <marking:Marking>
                    <marking:Controlled_Structure>//node() | //@*</marking:Controlled_Structure>
                    <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='RED'/>
                </marking:Marking>
            </stix:Handling>
        </stix:STIX_Header>
        <stix:Indicators>
            <stix:Indicator id="example:indicator-08174fbc-115f-46d6-890b-4214fbd8c3e4" timestamp="2016-03-30T15:58:30.662000Z" xsi:type='indicator:IndicatorType'>
                <indicator:Title>Test</indicator:Title>
                <stix:Handling>
                    <marking:Marking>
                        <marking:Controlled_Structure>../../../descendant-or-self::node() | ../../../descendant-or-self::node()/@*</marking:Controlled_Structure>
                        <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='AMBER'/>
                    </marking:Marking>
                </stix:Handling>
            </stix:Indicator>
        </stix:Indicators>
    </stix:STIX_Package>

Parse the document and return all markings present in the document.

.. testcode::

    import stixmarx

    container = stixmarx.parse("doc.xml")
    package = container.package

    print container.get_markings(package, descendants=True)

Parsing Observable Markings
---------------------------

Since CybOX observables do not have their own ``<Handling>`` element, they must be marked by a STIX element that contains them. In stixmarx, this is done via a top ``<STIX_Header>``-level XPath that applies to the observable. It is not required for an Observable to have an ``id`` to be marked.

Here is an example with an observable:

.. testcode::

    <stix:STIX_Package
        xmlns:example="http://example.com"
        xmlns:AddressObj="http://cybox.mitre.org/objects#AddressObject-2"
        xmlns:cybox="http://cybox.mitre.org/cybox-2"
        xmlns:indicator="http://stix.mitre.org/Indicator-2"
        xmlns:marking="http://data-marking.mitre.org/Marking-1"
        xmlns:stix="http://stix.mitre.org/stix-1"
        xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="example:Package-9cec4a05-3e12-45aa-acda-0c514aeec88e" version="1.2">
        <stix:STIX_Header>
            <stix:Handling>
                <marking:Marking>
                    <marking:Controlled_Structure>../../../../stix:Observables[1]/descendant-or-self::node() | ../../../../stix:Observables[1]/descendant-or-self::node()/@*</marking:Controlled_Structure>
                    <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='RED'/>
                </marking:Marking>
            </stix:Handling>
        </stix:STIX_Header>
        <stix:Observables cybox_major_version="2" cybox_minor_version="1" cybox_update_version="0">
            <cybox:Observable id="example:Observable-70b700de-bf18-42c6-9ff1-b6b75ecc9873">
                <cybox:Object id="example:Address-d828f9b1-0069-4448-b3ad-81bf57075ff5">
                    <cybox:Properties xsi:type="AddressObj:AddressObjectType">
                        <AddressObj:Address_Value>10.0.0.1</AddressObj:Address_Value>
                    </cybox:Properties>
                </cybox:Object>
            </cybox:Observable>
        </stix:Observables>
    </stix:STIX_Package>
   
When this document (named ``doc.xml`` below) is parsed, the observable marking can be read:
   
.. testcode::

    import stixmarx

    container = stixmarx.parse("doc.xml")
    stix_package = container.package
    observable = stix_package.observables[0]

    print container.get_markings(observable)

Parsing Field-Level Markings
----------------------------

To access field level markings from a parsed document, use their corresponding attribute.

.. testcode::

    <stix:STIX_Package
        xmlns:example="http://example.com"
        xmlns:indicator="http://stix.mitre.org/Indicator-2"
        xmlns:marking="http://data-marking.mitre.org/Marking-1"
        xmlns:stix="http://stix.mitre.org/stix-1"
        xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="example:Package-3972115d-3e88-4688-8dff-6208bcf1db55" version="1.2">
        <stix:Indicators>
            <stix:Indicator id="example:indicator-08174fbc-115f-46d6-890b-4214fbd8c3e4" timestamp="2016-03-30T15:58:30.662000Z" xsi:type='indicator:IndicatorType'>
                <indicator:Title>Test</indicator:Title>
                <indicator:Handling>
                    <marking:Marking>
                        <marking:Controlled_Structure>../../../indicator:Title[1]/self::node()</marking:Controlled_Structure>
                        <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='RED'/>
                    </marking:Marking>
                </indicator:Handling>
            </stix:Indicator>
        </stix:Indicators>
    </stix:STIX_Package>

When this document is parsed, the field level markings can be read:

.. testcode::

    import stixmarx

    container = stixmarx.parse("doc.xml")
    package = container.package
    indicator = package.indicators[0]

    print container.get_markings(indicator.title)
    # Note: Only the Title node is marked! Not its text.

Parsing Text or Attribute Markings
----------------------------------

To access text or attribute markings from a parsed document, use their corresponding property.

.. testcode::

    <stix:STIX_Package
        xmlns:example="http://example.com"
        xmlns:indicator="http://stix.mitre.org/Indicator-2"
        xmlns:marking="http://data-marking.mitre.org/Marking-1"
        xmlns:stix="http://stix.mitre.org/stix-1"
        xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" id="example:Package-3972115d-3e88-4688-8dff-6208bcf1db55" version="1.2">
        <stix:Indicators>
            <stix:Indicator id="example:indicator-08174fbc-115f-46d6-890b-4214fbd8c3e4" timestamp="2016-03-30T15:58:30.662000Z" xsi:type='indicator:IndicatorType'>
                <indicator:Title>Test Title</indicator:Title>
                <indicator:Description>Test Description</indicator:Description>
                <indicator:Handling>
                    <marking:Marking>
                        <marking:Controlled_Structure>../../../indicator:Description[1]/text()</marking:Controlled_Structure>
                        <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='RED'/>
                    </marking:Marking>
                    <marking:Marking>
                        <marking:Controlled_Structure>../../../@timestamp</marking:Controlled_Structure>
                        <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='AMBER'/>
                    </marking:Marking>
                </indicator:Handling>
            </stix:Indicator>
        </stix:Indicators>
    </stix:STIX_Package>

When this document is parsed, the field level markings can be read:

.. testcode::

    import stixmarx

    container = stixmarx.parse("doc.xml")
    package = container.package
    indicator = package.indicators[0]

    print container.get_markings(indicator.description.value)
    print container.get_markings(indicator.timestamp)
