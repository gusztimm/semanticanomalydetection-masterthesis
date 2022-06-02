from knowledgebase_population import linguisticpopulator, knowledgebasehandler, knowledgebasehandler_original
from knowledgebase.knowledgerecord import Dataset, KnowledgeRecord, Observation


kb_new = knowledgebasehandler.populate_verbocean()


limit = 100000000000000000

print(f'New KR with objects, first {limit} records:')
i=1
for key in kb_new.record_map.keys():
    kr = kb_new.record_map[key]
    if len(kr.source)>1:
        i+=1
        print(kr)
        

    if i>limit:
        break

print(f'records with more than one SRC: {i}')
"""
print(f'Old vanilla KB with VO only, first {limit} records:')
j=0

for key in kb_old.record_map.keys():
    kb_old.record_map[key]
    j+=1

    if j>limit:
        break
"""