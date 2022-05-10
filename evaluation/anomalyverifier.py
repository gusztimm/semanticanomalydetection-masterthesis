from collections import Counter

from evaluation.evaluation_result import LogEvaluationResults
from knowledgebase.knowledgerecord import Observation


def is_true_anomaly(anomaly, orig_log):
    if anomaly.anomaly_type == Observation.ORDER:
        # if event2 never follows event1 in the original log, it is a true order anomaly
        return not has_follows_relation(anomaly.event1, anomaly.event2, orig_log)
    if anomaly.anomaly_type == Observation.XOR:
        # if event1 and event2 always exclude each other in the original log, it is a true exclusion anomaly
        return has_exclusion_relation(anomaly.event1, anomaly.event2, orig_log)
    if anomaly.anomaly_type == Observation.CO_OCC:
        # if event1 always co-occurs with event2 in the original log, it is a true co-occurrence anomaly
        return has_cooccurrence_relation(anomaly.event1, anomaly.event2, orig_log)
    return False


def has_cooccurrence_relation(event1, event2, log):
    # checks if every trace that has event1 also has event2
    for variant in log.get_variants():
        has_event1 = False
        has_event2 = False
        for event in variant:
            if event == event1:
                has_event1 = True
            if event == event2:
                has_event2 = True
        if has_event1 and not has_event2:
            return False
    return True


def has_exclusion_relation(event1, event2, log):
    # checks if there is a trace where event1 and event2 both occur
    for variant in log.get_variants():
        has_event1 = False
        has_event2 = False
        for event in variant:
            if event == event1:
                has_event1 = True
            if event == event2:
                has_event2 = True
        if has_event1 and has_event2:
            return False
    return True


def has_follows_relation(event1, event2, log):
    # checks if there is a trace where event1 occurs before event2 in the log
    for variant in log.get_variants():
        for i in range(len(variant) - 1):
            if variant[i] == event1:
                for j in range(i + 1, len(variant)):
                    if variant[j] == event2:
                        return True
    return False


def analyze_anomaly_correctness(log_result, anomaly_counts, orig_simple_log):
    true_anomalies = [(anomaly, anomaly_counts[anomaly]) for anomaly in anomaly_counts.keys()
                      if is_true_anomaly(anomaly, orig_simple_log)]
    false_anomalies = [(anomaly, anomaly_counts[anomaly]) for anomaly in anomaly_counts.keys()
                      if not is_true_anomaly(anomaly, orig_simple_log)]
    return true_anomalies, false_anomalies


def analyze_trace_accuracy(detected_variants, orig_simple_log, noisy_simple_log):
    orig_variants = orig_simple_log.get_variants()
    trace_results = Counter()
    for variant in detected_variants:
        if variant not in orig_variants:
            trace_results["trace_tp"] += noisy_simple_log.variant_count(variant)
            trace_results["variant_tp"] += 1
        else:
            trace_results["trace_fp"] += noisy_simple_log.variant_count(variant)
            trace_results["variant_fp"] += 1
    return trace_results
