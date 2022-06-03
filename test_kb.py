from knowledgebase_population import linguisticpopulator, knowledgebasehandler, knowledgebasehandler_original
from knowledgebase.knowledgerecord import Dataset, KnowledgeRecord, Observation

kb_new = knowledgebasehandler.populate_verbocean()

#empty dict
collection = {}

# ITERATE over KB
for key in kb_new.record_map.keys():
    kr = kb_new.record_map[key]


# PRINT collection
limit = 100
i=1

for key, kr in collection.items():
    
    if len(kr.src_set) > 1:
        i+=1
        print(kr)

print(i)