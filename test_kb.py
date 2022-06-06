from knowledgebase_population import linguisticpopulator, knowledgebasehandler
from knowledgebase.knowledgerecord import Dataset, KnowledgeRecord, Observation
import pickle
import sys
import matplotlib.pyplot as plt
import numpy as np


class Object:

    def __init__(self, set):
        self.set = set


o1 = Object({'a',1})
o2 = Object({'a',2})
o3 = Object({'a',3})
o4 = Object({'a',4})
