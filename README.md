# Incorporation of commonsense knowledge resources for Semantic Anomaly Detection in Process Mining

This is the code repository of the Master Thesis written by Gusztáv Megyesi, submitted to the Data and Web Science Group of the University of Mannheim.

## Structure

The repository is split into two branches:

<b>main</b> This branch encompasses the code required to reproduce all results, except for tasks associated with Anomaly Classification

<b>semanticanomalydetection-anomalyclassification</b> This branch includes the code to reproduce the results for the Anomaly Classification tasks.

## Knowledge extraction

Extraction scripts and extracted knowledge records are stored in `knowledgebase_population/additional_kb/`

### ConceptNet

<b>`kb_conceptnet.ser`</b>: ConceptNet knowledge records extracted as dictionary
<b>`conceptnet_crawler.py`</b>: Crawler methods to retrieve JSON files from the ConceptNet API<br>
<b>`conceptnet_extractor.py`</b>: Retrieves and parses JSON files using the ConceptNet crawler, based on the activities in the synthetic BPMAI logs and their synonyms, stores output as text file<br>
<b>`conceptnet_crawler.py`</b>: Creates .ser file from the extracted ConceptNet content stored as text file<br>

### Atomic

<b>`kb_atomic.ser`</b>: Atomic knowledge records extracted as dictionary<br>
<b>`atomic_extractor.py`</b>: Parses Atomic flat files and outputs knowledge records as .ser file

### Knowledge base population

Knowledge base is populated using the corresponding method in the script `knowledgebase_population/linguisticpopulator.py`. This file replaces the original `verboceanpopulator.py` but preserves its structure.

## Reasoning engine improvements

This section provides a brief overview on the implementation of each improvement strategy, respectively. All of them, except Anomaly Classification, can be turned on using the respective flag when instantiating a respective Configuration object (c.f. `anomalydetection/configuration.py`).

### Business Object Matching

KnowledgeRecord object now contains an object to represent an associated business object. In the KnowledgeBase class, get_* functions have been added or modified to retrieve knowledge records belonging to certain object (c.f. 'obj' parameter). The anomaly checking functions (has_xxx_violation etc.) have been extended to consider whether an object parameter was supplied.

In the AnomalyDetector class, the function detect_anomalies_for_pair has been modified in a way that the object is extracted from the event label and supplied to the anomaly checking functions in the KnowledgeBase class.

<b>Main files affected:</b><br>
`knowledgebase/knowledgerecord.py`<br>
`knowledgebase/knowledgebase.py`<br>
`anomalydetection/anomalydetector.py`

### Knowledge Record Ranking

In the KnowledgeBase class, the anomaly checking functions (has_xxx_violation etc.) have been extended with an if-clause checking for the filter_heuristics_rank option. If it is active, then the ranks are collected for all knowledge records supporting and contradicting concerning a certain verb pair. The anomaly is only reported if the rank of supporting records is lower (=better) than the rank of contradicting records.

The ranks are stored in the KnowledgeBase class.

<b>Main files affected:</b><br>
`knowledgebase/knowledgebase.py`<br>

### Knowledge Record Confidence

In the KnowledgeBase class, the anomaly checking functions (has_xxx_violation etc.) have been extended with an if-clause checking for the filter_heuristics_cscore option. If it is active, then the confidence scores are collected for all knowledge records supporting and contradicting concerning a certain verb pair. The anomaly is only reported if the score of supporting records is higher than the rank of contradicting records.

<b>Main files affected:</b><br>
`knowledgebase/knowledgebase.py`<br>
`knowledgebase_population/linguisticpopulator.py` (for score calculation)<br>
`knowledgebase/similaritycomputer.py` (for calculating similarity-discounted scores)

### Anomaly Classification

The AnomalyDetector class has been modified in a way that the confidence scores triggering an anomaly are captured and supplied to the Anomaly object. The scores are initially reported using the anomaly checking functions (has_xxx_violation etc.).

The anomaly classification is executed by running anomalyclassifier.py in the root folder, which analyzes the scores contained in the Anomaly objects. To make all necessary calculations, a .ser file is required as input, which is produced by the synthetic evaluation as output.

<b>Main files affected:</b><br>
`anomalyclassifier.py`<br>
`anomalydetection/anomaly.py`<br>
`anomalydetection/anomalydetector.py`<br>
`knowledgebase/knowledgebase.py`<br>

## Evaluation

The evaluation results are stored in the `output` folder, in separate folders for each approach.


## Installation

The implementation has been developed using Python 3.7.12. It is recommended to create a virtual environment and resolve the dependencies specified in requirements.txt, e.g. using `pip install -r requirements.txt`. Note that due to the incompatibility of some components, the approach does not run under Windows.

## Reproduction of results

The results of this thesis are reproducible by executing `synthetic_evaluation.py` or `realworld_evaluation.py` and setting the corresponding parameters in the Configuration object. The new parameters added in this thesis are the following:

<b>`limit_bos`</b> BO-matching: only use knowledge records which are object independent or correspond to object
<b>`filter_heuristics_rank`</b> Conflict resolution based on provenance of knowledge records
<b>`filter_heuristics_cscore`</b> Conflict resolution based on confidence score of knowledge records

To reproduce the Anomaly Classification results, run `anomalyclassifier.py` in the branch <b>semanticanomalydetection-anomalyclassification</b>. It analyzes the raw results (.ser file) of anomaly detection runs with the extended KB which are stored in this repo. Therefore, there is no need to re-run the anomaly detection itself.
