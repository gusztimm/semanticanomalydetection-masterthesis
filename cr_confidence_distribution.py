from knowledgebase_population import linguisticpopulator, knowledgebasehandler
from knowledgebase.knowledgerecord import Dataset, KnowledgeRecord, Observation
from sklearn.preprocessing import MinMaxScaler

import os
import random
import sys
import pandas as pd
import matplotlib.pyplot as plt


kb_ser_dir = "input/bpmai/extracted_records"
kb_new = knowledgebasehandler.populate_from_ser_fragments(kb_ser_dir, case_names=None)

conf_verbocean = []
conf_conceptnet = []

for key in kb_new.record_map.keys():
    kr = kb_new.record_map[key]

    src_set = kr.source

    for src in src_set:

        dataset = src[0]
        conf = src[1]

        if dataset == Dataset.CONCEPTNET:
            conf_conceptnet.append(min(conf,1))

        if dataset == Dataset.VERBOCEAN:
            conf_verbocean.append(conf)

d_conceptnet = {'conceptnet': conf_conceptnet}
d_verbocean = {'verbocean': conf_verbocean} 
df_conceptnet = pd.DataFrame(data=d_conceptnet)
df_verbocean = pd.DataFrame(data=d_verbocean)

print(df_conceptnet.describe())
print(df_verbocean.describe())

plt.hist(conf_conceptnet, bins=100)
plt.gca().set(title='ConceptNet Conf Score Histogram', xlabel='Conf score', ylabel='Frequency')
plt.show()

plt.hist(conf_verbocean, bins=100)
plt.gca().set(title='VerbOcean Conf Score Histogram', xlabel='Conf score', ylabel='Frequency')
plt.show()