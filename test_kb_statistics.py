from stringprep import c6_set
from knowledgebase_population import linguisticpopulator, knowledgebasehandler
from knowledgebase.knowledgerecord import Dataset, KnowledgeRecord, Observation
from knowledgebase.knowledgebase import KnowledgeBase
from knowledgebase.similaritycomputer import SemanticSimilarityComputer, SynonymSimilarityComputer, SimMode
from anomalydetection.configuration import Configuration
import pickle
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

kb_ser_dir = "input/bpmai/extracted_records"
kb_new = knowledgebasehandler.populate_from_ser_fragments(kb_ser_dir, case_names=None)
#kb_new = knowledgebasehandler.populate_knowledge_base(use_bpmai=True, use_verbocean=True)

rank_collection=[]
all_confidence_collection=[]


# ITERATE over KB
for key in kb_new.record_map.keys():
    kr = kb_new.record_map[key]

    #rank = kb_new.get_record_rank(kr.verb1, kr.verb2, kr.record_type, kr.obj)
    #rank_collection.append(rank)

    all_confidence_collection.append(kr.normconf)
    

plt.hist(all_confidence_collection, bins=50)
plt.gca().set(title='Score Histogram', xlabel='Score', ylabel='Frequency')
plt.show()

