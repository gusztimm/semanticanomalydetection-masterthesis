import datetime
from knowledgebase_population import linguisticpopulator, knowledgebasehandler, knowledgebasehandler_original
from knowledgebase.knowledgerecord import Dataset, KnowledgeRecord, Observation
import os
import random



class KnowledgeRecord_Light:

    def __init__(self, verb1, verb2, record_type, obj=set(), src_set=set()):
        # Instance of KnowledgeRecord consists of two verbs and optionally the specification of an object
        self.verb1 = verb1
        self.verb2 = verb2
        self.record_type = record_type
        self.src_set = src_set
        self.obj = obj

    def __repr__(self):
        return f"{str(self.record_type)}: {self.verb1} - {self.verb2} object: {self.obj} src: {self.src_set}"



kb_ser_dir = "input/bpmai/extracted_records"
kb_new = knowledgebasehandler.populate_from_ser_fragments(kb_ser_dir, case_names=None)
#kb_new = knowledgebasehandler.populate_knowledge_base(use_bpmai=True, use_verbocean=True)


#empty dict
collection = {}

# ITERATE over KB
for key in kb_new.record_map.keys():
    kr = kb_new.record_map[key]

    verb1 = kr.verb1
    verb2 = kr.verb2
    record_type = kr.record_type
    obj = kr.obj
    src_set = {src_tuple[0] for src_tuple in kr.source}
    
    # fresh one
    if (verb1, verb2, record_type) not in collection:
        collection[(verb1, verb2, record_type)] = KnowledgeRecord_Light(verb1, verb2, record_type, {obj}, src_set)

    # already exists
    else:
        existing_kr = collection[(verb1, verb2, record_type)]
        new_kr = existing_kr

        # add object
        new_kr.obj.add(obj)
        
        # add src dataset
        for src in src_set:
            new_kr.src_set.add(src)

        # update object
        collection[(verb1, verb2, record_type)] = new_kr


# PRINT collection
limit = 100
i=0
j=0

for key, kr in collection.items():
    j+=1
    if len(kr.src_set) > 1:
        i+=1
        print(kr)

print(f'KR with more than one source: {i}')
print(f'KR total: {j}')