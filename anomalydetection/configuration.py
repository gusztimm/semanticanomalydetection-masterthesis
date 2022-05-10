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
                 max_count=sys.maxsize  # set the maximal times an anomaly may occur in an event log
                 ):
        self.use_bert_parser = use_bert_parser
        self.equal_bos = equal_bos
        self.split_loops = split_loops
        self.sim_mode = sim_mode
        self.match_one = match_one
        self.sim_threshold = sim_threshold
        self.use_kb_heuristics = kb_heuristics
        self.min_support = min_support
        self.max_count = max_count

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
        if self.min_support > 1:
            res = res + "_min_support:" + str(self.min_support)
        if self.max_count < sys.maxsize:
            res = res + "_max_count:" + str(self.max_count)
        return res

    def tofilename(self):
        return str(self).replace('_', '').replace(':', "_")
