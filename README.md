# Incorporation of commonsense knowledge resources for Semantic Anomaly Detection in Process Mining

This is the code repository of the Master Thesis written by Gusztáv Megyesi, submitted to the Data and Web Science Group of the University of Mannheim.

## Structure

The repository is split into two branches:

<b>main</b> This branch encompasses the code required to reproduce all results, except for tasks associated with Anomaly Classification

<b>semanticanomalydetection-anomalyclassification</b> This branch includes the code to reproduce the results for the Anomaly Classification tasks.

## Knowledge extraction

Extraction scripts and extracted knowledge records are stored in knowledgebase_population/additional_kb/

### ConceptNet

<b>kb_conceptnet.ser</b>: ConceptNet knowledge records extracted as dictionary

<b>conceptnet_crawler.py</b>: Crawler methods to retrieve JSON files from the ConceptNet API<br>
<b>conceptnet_extractor.py</b>: Retrieves and parses JSON files using the ConceptNet crawler, based on the activities in the synthetic BPMAI logs and their synonyms, stores output as text file<br>
<b>conceptnet_crawler.py</b>: Creates .ser file from the extracted ConceptNet content stored as text file<br>

### Atomic

<b>kb_atomic.ser</b>: Atomic knowledge records extracted as dictionary<br>
<b>atomic_extractor.py</b>: Parses Atomic flat files and outputs knowledge records as .ser file

### Knowledge base population

Knowledge base is populated using the corresponding method in the script knowledgebase_population/linguisticpopulator.py. This file replaces the original verboceanpopulator.py but preserves its structure.

## Reasoning engine improvements

This section provides a brief overview on the implementation of each improvement strategy, respectively. All of them, except Anomaly Classification, can be turned on using the respective flag when instantiating a respective Configuration object (c.f. anomalydetection/configuration.py).

### Business Object Matching

KnowledgeRecord object now contains an object to represent an associated business object. In the KnowledgeBase class, get_* functions have been added or modified to retrieve knowledge records belonging to certain object (c.f. 'obj' parameter). The anomaly checking functions (has_xxx_violation etc.) have been extended to consider whether an object parameter was supplied.

In the AnomalyDetector class, the function detect_anomalies_for_pair has been modified in a way that the object is extracted from the event label and supplied to the anomaly checking functions in the KnowledgeBase class.

<b>Main files affected:</b><br>
knowledgebase/knowledgerecord.py<br>
knowledgebase/knowledgebase.py<br>
anomalydetection/anomalydetector.py

### Knowledge Record Ranking

In the KnowledgeBase class, the anomaly checking functions (has_xxx_violation etc.) have been extended with an if-clause checking for the filter_heuristics_rank option. If it is active, then the ranks are collected for all knowledge records supporting and contradicting concerning a certain verb pair. The anomaly is only reported if the rank of supporting records is lower (=better) than the rank of contradicting records.

### Knowledge Record Confidence

### Anomaly Classification
