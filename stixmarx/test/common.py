# Copyright (c) 2015, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

"""
Code that is common to the unit test modules.
"""

STIX_XML_TEMPLATE_GLOBAL_AND_COMPONENT = \
"""
<stix:STIX_Package
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
        <stix:Indicator id="example:indicator-f0a233e2-6d21-4ea6-bf8c-ed4f57e10d31" timestamp="2015-02-26T21:00:37.454000+00:00" xsi:type='indicator:IndicatorType'>
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

STIX_XML_TEMPLATE_EMBEDDED_OBSERVABLE = \
"""
<stix:STIX_Package 
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
    <stix:STIX_Header>
        <stix:Handling>
            <marking:Marking>
                <marking:Controlled_Structure>{0}</marking:Controlled_Structure>
                <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='RED'/>
            </marking:Marking>
        </stix:Handling>
    </stix:STIX_Header>
    <stix:Indicators>
        <stix:Indicator id="example:indicator-44c5bff4-ecb7-4110-96af-27b1e964b815" timestamp="2015-03-05T16:19:54.603000+00:00" xsi:type='indicator:IndicatorType'>
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
                    <marking:Controlled_Structure>{1}</marking:Controlled_Structure>
                    <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color='AMBER'/>
                </marking:Marking>
            </indicator:Handling>
        </stix:Indicator>
    </stix:Indicators>
</stix:STIX_Package>
"""