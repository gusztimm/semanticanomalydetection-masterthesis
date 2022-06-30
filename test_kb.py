from knowledgebase_population import linguisticpopulator, knowledgebasehandler
from knowledgebase.knowledgerecord import Dataset, KnowledgeRecord, Observation
from knowledgebase.knowledgebase import KnowledgeBase
from knowledgebase.similaritycomputer import SemanticSimilarityComputer, SynonymSimilarityComputer, SimMode
from anomalydetection.configuration import Configuration
import pickle
import sys
import matplotlib.pyplot as plt
import numpy as np
"""
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
"""
sim_comp_ser_file = "input/similarity/semanticsimcomputer.ser"
kb_ser_dir = "input/bpmai/extracted_records"

kb_new = KnowledgeBase()
kb_new = knowledgebasehandler.populate_from_ser_fragments(kb_ser_dir)

limit = 100
i=1

catalog = {
    Dataset.VERBOCEAN:{Observation.XOR:0, Observation.ORDER:0, Observation.CO_OCC:0},
    Dataset.CONCEPTNET:{Observation.XOR:0, Observation.ORDER:0, Observation.CO_OCC:0},
    Dataset.ATOMIC:{Observation.XOR:0, Observation.ORDER:0, Observation.CO_OCC:0},
    Dataset.BPMAI:{Observation.XOR:0, Observation.ORDER:0, Observation.CO_OCC:0}
}

nr_object=0

for record in kb_new.record_map.values():
    relation = record.record_type

    for src in record.source:
        dataset = src[0]
        
        catalog[dataset][relation]+=1

        if record.obj!='':
            nr_object+=1

print(catalog)
print(f'{nr_object} records have an object')


sys.exit()

config = Configuration(sim_mode=SimMode.SYNONYM, filter_heuristics_cscore=True,match_one=False)

sim_computer_semantic = SemanticSimilarityComputer(match_one=config.match_one,
                                                  sim_threshold=config.sim_threshold,
                                                  compute_sim_per_log=False)
sim_computer_synonym = SynonymSimilarityComputer(match_one=config.match_one)

sim_computer = sim_computer_semantic

print(sim_computer.sim_mode)

if sim_computer.sim_mode == SimMode.SEMANTIC_SIM:
    kb_verbs, dictionary, docsim_index = pickle.load(open(sim_comp_ser_file, "rb"))
    sim_computer.set_loaded_similarities(kb_verbs, dictionary, docsim_index)

kb_new = knowledgebasehandler.populate_knowledge_base(use_bpmai=False, use_verbocean=True)


limit = 100
i=1

for key, record in kb_new.record_map.items():
    i+=1
    print(record)

    if i>limit:
        break

#similar_records = kb_new.get_similar_records_with_sim_value('approve','check',Observation.ORDER,sim_computer=sim_computer,obj='')

#for record in similar_records:
    #print(f'{record}\n')

#sim_accept = sim_computer.compute_semantic_sim_verbs_with_similarity_value('accept')
#sim_reject = sim_computer.compute_semantic_sim_verbs_with_similarity_value('reject')


