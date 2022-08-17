"""
This file is part of the repository belonging to the Master Thesis of Gusztáv Megyesi - MN 1526252
Title: Incorporation of Commonsense Knowledge Resources for Semantic Anomaly Detection in Process Mining
Submitted to the Data and Web Science Group - Prof. Dr. Han van der Aa - University of Mannheim in August 2022

The original version of this file has been downloaded from the repository belonging to the following paper:
H. van der Aa, A. Rebmann, and H. Leopold, “Natural language-based detection of semantic execution anomalies in event logs,” Information Systems, vol. 102, p. 101824, Dec. 2021.
The original repository is available at https://gitlab.uni-mannheim.de/processanalytics/semanticanomalydetection
"""

from knowledgebase.similaritycomputer import SimMode
import sys


class Configuration:

    def __init__(self,
                 use_bert_parser=True,  # use BERT parser or old school HMM parser (ALWAYS USE TRUE)
                 equal_bos=True,  # only detect anomalies between events with equal business objects (ALWAYS USE TRUE)
                 split_loops=False,  # should traces with recurring activities be split up?
                 sim_mode=SimMode.EQUAL,  # set the similarity mode (EQUAL, SYNONYM, SEMANTIC)
                 match_one=False,  # only one verb in a record can be a synonym/semantically similar verb (other equal)
                 sim_threshold=0.7,  # define the minimal required score for verbs to be considered semantically similar
                 kb_heuristics=False, # should kb records be filtered based on conflict resolution heuristics?
                 min_support=1,  # define the minimal confidence required for a record
                 max_count=sys.maxsize,  # set the maximal times an anomaly may occur in an event log
                 limit_bos=False, # GM-OBJ only use KR which are object independent or correspond to object
                 filter_heuristics_rank=False, # When kb-heuristics is set, consider ranking of different datasets
                 filter_heuristics_cscore = False, # When kb-heuristics is set, consider confidence score of KR
                 anomaly_classification = True # in this repo, always set to TRUE
                 ):
        self.use_bert_parser = use_bert_parser
        self.equal_bos = equal_bos
        self.split_loops = split_loops
        self.sim_mode = sim_mode
        self.match_one = match_one
        self.sim_threshold = sim_threshold
        self.use_kb_heuristics = kb_heuristics
        #GM-conflict_resolution
        self.filter_heuristics_rank = filter_heuristics_rank
        self.filter_heuristics_cscore = filter_heuristics_cscore

        self.min_support = min_support
        self.max_count = max_count
        self.limit_bos = limit_bos # GM-OBJ

        #GM-anomaly_classification
        self.anomaly_classification = anomaly_classification


    def __repr__(self):
        res = "sim_mode:" + str(self.sim_mode)
        if self.sim_mode == SimMode.SEMANTIC_SIM:
            res = res + "_sim_thres:" + str(self.sim_threshold)
        if self.match_one:
            res = res + "_match_one:" + str(self.match_one)
        if self.split_loops:
            res = res + "_split_loops:" + str(self.split_loops)
        if self.use_kb_heuristics:
            res = res + "_kb_heuristics:" + str(self.use_kb_heuristics)
        if self.filter_heuristics_rank:
            res = res + "_filter_heuristics_rank:" + str(self.filter_heuristics_rank)
        if self.filter_heuristics_cscore:
            res = res + "_filter_heuristics_cscore:" + str(self.filter_heuristics_cscore)
        if self.min_support > 1:
            res = res + "_min_support:" + str(self.min_support)
        if self.max_count < sys.maxsize:
            res = res + "_max_count:" + str(self.max_count)
        if self.limit_bos:
            res = res + "_limit_bos:" + str(self.limit_bos)
        if self.anomaly_classification:
            res = res + "_anomaly_classification:" + str(self.anomaly_classification)
        return res

    def tofilename(self):
        return str(self).replace('_', '').replace(':', "_")
