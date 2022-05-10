import csv
import random
import time
import pickle
from pm4py.algo.discovery.heuristics import factory as heuristics_miner
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
import evaluation.anomalyverifier as verifier
from evaluation import simple_log_collection, evaluation_result
from evaluation.evaluation_result import LogEvaluationResults, FullEvaluationResult
from labelparser import label_utils

import synthetic_evaluation


def apply_bezerra_naive_baseline(simple_log, threshold=0.02):
    max_count = threshold * simple_log.total_traces()
    return [variant for variant in
            simple_log.get_variants() if simple_log.variant_count(variant) <= max_count]


def apply_bezerra_sample_baseline(simple_log, sample_fraction, threshold=0.02):
    # select random log sample
    variants = simple_log.get_variants()
    random.shuffle(variants)
    sampled_log = [simple_log_collection.string_sequence_to_trace(variant) for variant in
                   variants[0:round(len(variants) * sample_fraction)]]
    # discover log from sample
    net, im, fm = heuristics_miner.apply(sampled_log)

    # identify candidate variants based on frequencies
    max_count = threshold * simple_log.total_traces()
    candidate_traces = [simple_log_collection.string_sequence_to_trace(variant) for variant in
                          simple_log.get_variants() if simple_log.variant_count(variant) <= max_count]
    replayed_traces = token_replay.apply(candidate_traces, net, im, fm)
    anomalous_variants = [trace_to_sequence(candidate_traces[i]) for i in range(0, len(replayed_traces)) if
                          not replayed_traces[i]["trace_is_fit"]]

    return anomalous_variants


def sanitize_event_labels(trace, event_key="concept:name"):
    return [{event_key: label_utils.sanitize_label(event[event_key])} for event in trace]


def trace_to_sequence(trace, event_key="concept:name"):
    return [event[event_key] for event in trace]


def run_baselines():
    orig_log_collection = pickle.load(open(synthetic_evaluation.orig_log_collection_file, "rb"))
    noisy_log_collection = pickle.load(open(synthetic_evaluation.noisy_log_collection_file, "rb"))
    log_names = list(noisy_log_collection.get_log_names())
    eval_results_naive_bl = FullEvaluationResult("naive baseline", repl=1)
    eval_results_sample_bl = FullEvaluationResult("sampled baseline", repl=1)
    done = 0
    for log_name in log_names:
        orig_simple_log = orig_log_collection.get_log(log_name)
        noisy_simple_log = noisy_log_collection.get_log(log_name)

        log_result_naive = LogEvaluationResults()
        naive_anomalies = apply_bezerra_naive_baseline(noisy_simple_log, threshold=0.05)
        log_result_naive.trace_results  = verifier.analyze_trace_accuracy(naive_anomalies, orig_simple_log, noisy_simple_log)
        eval_results_naive_bl.add_log_result(log_name, log_result_naive)

        log_result_sample = LogEvaluationResults()
        sampled_anomalies = apply_bezerra_sample_baseline(noisy_simple_log, sample_fraction=0.7, threshold=0.05)
        log_result_sample.trace_results = verifier.analyze_trace_accuracy(sampled_anomalies, orig_simple_log, noisy_simple_log)
        eval_results_sample_bl.add_log_result(log_name, log_result_sample)

        done += 1
        print(log_name, done, "done", log_result_sample.trace_results)

    print('\nnaive BL:')
    eval_results_naive_bl.print_trace_results()
    print('\n sampled BL')
    eval_results_sample_bl.print_trace_results()

    baseline_file = "output/baseline_results_" + time.strftime("%Y%m%d%H%M%S") + ".txt"
    with open(baseline_file, 'w') as output_file:
        writer = csv.writer(output_file, delimiter=';')
        writer.writerow(evaluation_result.trace_result_header)
        writer.writerow(eval_results_naive_bl.trace_result_array())
        writer.writerow(eval_results_sample_bl.trace_result_array())

run_baselines()
print('done')
