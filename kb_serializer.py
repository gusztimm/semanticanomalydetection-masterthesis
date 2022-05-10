
import os
import pickle
import random
import sys
"""
myDir = os.getcwd()
sys.path.append('home/gumegyes/semanticanomalydetection/semanticanomalydetection-masterthesis/knowledgebase_population')
sys.path.append('home/gumegyes/semanticanomalydetection/semanticanomalydetection-masterthesis/knowledgebase_population/additional_kb')
"""

from knowledgebase_population import knowledgebasehandler as kb_handler
from knowledgebase.similaritycomputer import SimMode, SimilarityComputer, SemanticSimilarityComputer, \
    SynonymSimilarityComputer
from anomalydetection.configuration import Configuration


config = Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.5, split_loops=True)

kb = kb_handler.populate_verbocean()
kb.min_support = config.min_support
kb.apply_filter_heuristics = config.use_kb_heuristics

with open('input/serializedkbs/full_kb_vn_co.ser','wb') as pickle_writer:
    pickle.dump(kb,pickle_writer)