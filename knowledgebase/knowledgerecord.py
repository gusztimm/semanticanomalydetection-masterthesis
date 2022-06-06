from enum import Enum

"""
@GM: object property added
"""

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

    def __repr__(self):
        out_object = self.obj
        if out_object == '':
            out_object = '[E]'
        
        #return str(self.record_type) + ": " + self.verb1 + " - " + self.verb2 + " object: " + out_object + " count: " + str(self.count) + " source: " + self.source
        return f"{str(self.record_type)}: {self.verb1} - {self.verb2} object: {out_object} count: {str(self.count)} src: {self.source} normconf: {self.normconf}"
