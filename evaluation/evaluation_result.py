import sys
from collections import Counter
from prettytable import PrettyTable

from knowledgebase.knowledgerecord import Observation

result_header = ["config", "replication",
                 "tp", "fp", "micro prec", "macro prec",
                 "tp (xor)", "fp (xor)", "micro prec (xor)", "macro prec (xor)",
                 "tp (order)", "fp (order)", "micro prec (order)", "macro prec (order)",
                 "tp (co-occ)", "fp (co-occ)", "micro prec (co-occ)", "macro prec (co-occ)",
                 "tp (abs)", "fp (abs)", "micro prec (abs)", "macro prec (abs)",
                 "tp (abs xor)", "fp (abs xor)", "micro prec (abs xor)", "macro prec (abs xor)",
                 "tp (abs order)", "fp (abs order)", "micro prec (abs order)", "macro prec (abs order)",
                 "tp (abs co-occ)", "fp (abs co-occ)", "micro prec (abs co-occ)", "macro prec (abs co-occ)",
                 "tp (variant)", "fp (variant)", "micro prec (variant)", "macro prec (variant)",
                 "tp (traces)", "fp (traces)", "micro prec (traces)", "macro prec (traces)",
                 "runtime (h:mm:ss.ms)"
                 ]

trace_result_header = result_header[0:2] + result_header[-9:]


class FullEvaluationResult:
    def __init__(self, config, repl=0):
        self.config = config
        self.repl = repl
        self.log_result_map = {}
        self.runtime = 0

    def add_log_result(self, log_name, log_result):
        self.log_result_map[log_name] = log_result

    def count_total_tp_and_fp(self, unique, obs_type=None, max_count=sys.maxsize):
        tp = sum([log_result.count_tp(unique, obs_type, max_count) for log_result in self.log_result_map.values()])
        fp = sum([log_result.count_fp(unique, obs_type, max_count) for log_result in self.log_result_map.values()])
        return tp, fp

    def count_total_trace_results(self):
        trace_results = Counter()
        for log_result in self.log_result_map.values():
            trace_results += log_result.trace_results
        return trace_results

    def compute_macro_precision(self, unique, obs_type=None, max_count=sys.maxsize):
        log_precisions = [precision(*log_result.tp_and_fp(unique, obs_type, max_count))
                          for log_result in self.log_result_map.values()]
        return sum(log_precisions) / len(log_precisions)

    def compute_trace_macro_precision(self, variant_level):
        log_precisions = [precision(*log_result.trace_tp_and_fp(variant_level))
                          for log_result in self.log_result_map.values()]
        return sum(log_precisions) / len(log_precisions)

    def to_array(self, max_count=sys.maxsize):
        types = [None, Observation.XOR, Observation.ORDER, Observation.CO_OCC]
        res = [str(self.config), self.repl]
        # unique anomalies
        for res_type in types:
            tp, fp = self.count_total_tp_and_fp(unique=True, obs_type=res_type, max_count=max_count)
            micro_prec = precision(tp, fp)
            macro_prec = self.compute_macro_precision(unique=True, obs_type=res_type, max_count=max_count)
            res = res + [tp, fp, micro_prec, macro_prec]

        # # absolute anomalies
        for res_type in types:
            tp, fp = self.count_total_tp_and_fp(unique=False, obs_type=res_type, max_count=max_count)
            micro_prec = precision(tp, fp)
            macro_prec = self.compute_macro_precision(unique=False, obs_type=res_type, max_count=max_count)
            res = res + [tp, fp, micro_prec, macro_prec]

        # # trace and variant-level
        trace_results = self.count_total_trace_results()
        tp, fp = trace_results["variant_tp"], trace_results["variant_fp"]
        micro_prec = precision(tp, fp)
        macro_prec = self.compute_trace_macro_precision(variant_level=True)
        res = res + [tp, fp, micro_prec, macro_prec]
        tp, fp = trace_results["trace_tp"], trace_results["trace_fp"]
        micro_prec = precision(tp, fp)
        macro_prec = self.compute_trace_macro_precision(variant_level=False)
        res = res + [tp, fp, micro_prec, macro_prec]
        #
        res = res + [self.runtime]
        return res

    def trace_result_array(self):
        return self.to_array()[0:2] + self.to_array()[-9:]

    def print_results(self):
        table = PrettyTable(result_header)
        # TODO: omit absolute results here?
        table.add_row(self.to_array())
        print(table)

    def print_trace_results(self):
        table = PrettyTable(trace_result_header)
        table.add_row(self.trace_result_array())
        print(table)


class LogEvaluationResults:
    def __init__(self):
        self.true_anomalies = []
        self.false_anomalies = []
        self.trace_results = Counter()

    def count_tp(self, unique, obs_type=None, max_count=sys.maxsize):
        if unique:
            return len([a for (a, c) in self.true_anomalies if matches_requirements(a, c, obs_type, max_count)])
            # return len([a for a in self.true_anomalies if obs_type is None or a[0].anomaly_type == obs_type])
        else:
            return sum([c for (a, c) in self.true_anomalies if matches_requirements(a, c, obs_type, max_count)])

    def count_fp(self, unique, obs_type=None, max_count=sys.maxsize):
        if unique:
            return len([a for (a, c) in self.false_anomalies if matches_requirements(a, c, obs_type, max_count)])
        else:
            return sum([c for (a, c) in self.false_anomalies if matches_requirements(a, c, obs_type, max_count)])

    def tp_and_fp(self, unique, obs_type=None, max_count=sys.maxsize):
        return self.count_tp(unique, obs_type, max_count), self.count_fp(unique, obs_type, max_count)

    def trace_tp_and_fp(self, variant_level):
        if variant_level:
            return self.trace_results['variant_tp'], self.trace_results['variant_fp']
        return self.trace_results['trace_tp'], self.trace_results['trace_fp']


def matches_requirements(anomaly, count, obs_type, max_count):
    return (obs_type is None or obs_type == anomaly.anomaly_type) and count <= max_count


def precision(tp, fp):
    if tp + fp == 0:
        return 1.0
    return tp / (tp + fp)
