from knowledgebase_population import linguisticpopulator, knowledgebasehandler
from knowledgebase.knowledgerecord import Dataset, KnowledgeRecord, Observation
from knowledgebase.knowledgebase import KnowledgeBase
import pickle
import sys
import matplotlib.pyplot as plt
import numpy as np

kb_ser_dir = "input/bpmai/extracted_records"
kb_new = knowledgebasehandler.populate_from_ser_fragments(kb_ser_dir, case_names=None)
#kb_new = knowledgebasehandler.populate_knowledge_base(use_bpmai=True, use_verbocean=True)

limit = 50
i=1
rank_collection=[]

# ITERATE over KB
for key in kb_new.record_map.keys():
    kr = kb_new.record_map[key]

    if len(kr.source)>1:
        continue

    rank = kb_new.get_record_rank(kr.verb1, kr.verb2, kr.record_type, kr.obj)
    rank_collection.append(rank)
    #print(f"{kr} - rank: {rank}")

plt.hist(rank_collection, bins=4)
plt.gca().set(title='Rank Histogram', xlabel='Rank', ylabel='Frequency')
plt.show()
