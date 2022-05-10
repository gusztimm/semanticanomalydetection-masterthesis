from knowledgebase_population import linguisticpopulator, knowledgebasehandler, knowledgebasehandler_original
from knowledgebase.knowledgerecord import KnowledgeRecord, Observation


kb_new = knowledgebasehandler.populate_verbocean()
limit = 100

print(f'New KR with objects, first {limit} records:')
i=0
for key in kb_new.record_map.keys():
    print(kb_new.record_map[key])
    i+=1

    if i>limit:
        break

"""
print(f'Old vanilla KB with VO only, first {limit} records:')
j=0

for key in kb_old.record_map.keys():
    kb_old.record_map[key]
    j+=1

    if j>limit:
        break
"""