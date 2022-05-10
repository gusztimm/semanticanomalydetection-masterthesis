from knowledgebase.knowledgerecord import Observation


class Anomaly:

    def __init__(self, anomaly_type, event1, event2, verb1, verb2, record_count):
        self.anomaly_type = anomaly_type
        self.event1 = event1
        self.event2 = event2
        self.verb1 = verb1
        self.verb2 = verb2
        self.record_count = record_count
        self.explanation = self.explain_anomaly()

    def explain_anomaly(self):
        if self.anomaly_type == Observation.ORDER:
            return "Order violation: " + self.event1 + " occurred before " + self.event2
        if self.anomaly_type == Observation.CO_OCC:
            return "Co-occ violation: " + self.event1 + " occurred without " + self.event2
        if self.anomaly_type == Observation.XOR:
            return "Exclusion violation: " + self.event1 + " occurred together with " + self.event2
        return ""

    def __repr__(self):
        return self.explanation

    def to_array(self):
        return [self.anomaly_type, self.event1, self.event2, self.verb1, self.verb2, self.record_count]

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()