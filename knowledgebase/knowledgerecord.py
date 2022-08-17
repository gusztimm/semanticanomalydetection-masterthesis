"""
This file is part of the repository belonging to the Master Thesis of Gusztáv Megyesi - MN 1526252
Title: Incorporation of Commonsense Knowledge Resources for Semantic Anomaly Detection in Process Mining
Submitted to the Data and Web Science Group - Prof. Dr. Han van der Aa - University of Mannheim in August 2022

The original version of this file has been downloaded from the repository belonging to the following paper:
H. van der Aa, A. Rebmann, and H. Leopold, “Natural language-based detection of semantic execution anomalies in event logs,” Information Systems, vol. 102, p. 101824, Dec. 2021.
The original repository is available at https://gitlab.uni-mannheim.de/processanalytics/semanticanomalydetection
"""

from enum import Enum

class Observation(Enum):
    XOR = 1,
    CO_OCC = 2,
    ORDER = 3

class Dataset(Enum):
    VERBOCEAN = 1,
    CONCEPTNET = 2,
    ATOMIC = 3,
    BPMAI = 4

class KnowledgeRecord:

    def __init__(self, verb1, verb2, record_type, obj='', count = 1, source=set()):
        # Instance of KnowledgeRecord consists of two verbs and optionally the specification of an object
        self.verb1 = verb1
        self.verb2 = verb2
        self.record_type = record_type
        self.count = count
        self.source = source
        self.obj = obj
        self.normconf = -1

    def increment_count(self, count):
        self.count += count

    def add_source(self, dataset, conf):
        self.source.add((dataset, conf))

    # Get rank of KnowledgeRecord object
    def get_knowledge_record_object_rank(self, dataset_ranking):
        record_ranks = set()

        for src in self.source:
            record_ranks.add(dataset_ranking[src[0]])

        return min(record_ranks)

    def __repr__(self):
        out_object = self.obj
        if out_object == '':
            out_object = '[E]'

        #return str(self.record_type) + ": " + self.verb1 + " - " + self.verb2 + " object: " + out_object + " count: " + str(self.count) + " source: " + self.source
        return f"{str(self.record_type)}: {self.verb1} - {self.verb2} object: {out_object} count: {str(self.count)} src: {self.source} normconf: {self.normconf}"
