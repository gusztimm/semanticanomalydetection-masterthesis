"""
This file is part of the repository belonging to the Master Thesis of Gusztáv Megyesi - MN 1526252
Title: Incorporation of Commonsense Knowledge Resources for Semantic Anomaly Detection in Process Mining
Submitted to the Data and Web Science Group - Prof. Dr. Han van der Aa - University of Mannheim in August 2022

The original version of this file has been downloaded from the repository belonging to the following paper:
H. van der Aa, A. Rebmann, and H. Leopold, “Natural language-based detection of semantic execution anomalies in event logs,” Information Systems, vol. 102, p. 101824, Dec. 2021.
The original repository is available at https://gitlab.uni-mannheim.de/processanalytics/semanticanomalydetection
"""

from knowledgebase.knowledgerecord import Observation


class Anomaly:

    def __init__(self, anomaly_type, event1, event2, verb1, verb2, record_count, score):
        self.anomaly_type = anomaly_type
        self.event1 = event1
        self.event2 = event2
        self.verb1 = verb1
        self.verb2 = verb2
        self.record_count = record_count
        self.score = score
        self.explanation = self.explain_anomaly()

    def explain_anomaly(self):
        if self.anomaly_type == Observation.ORDER:
            return "Order violation: " + self.event1 + " occurred before " + self.event2 + " score: " + str(self.score)
        if self.anomaly_type == Observation.CO_OCC:
            return "Co-occ violation: " + self.event1 + " occurred without " + self.event2 + " score: " + str(self.score)
        if self.anomaly_type == Observation.XOR:
            return "Exclusion violation: " + self.event1 + " occurred together with " + self.event2 + " score: " + str(self.score)
        return ""

    def __repr__(self):
        return self.explanation

    def to_array(self):
        return [self.anomaly_type, self.event1, self.event2, self.verb1, self.verb2, self.record_count]

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
