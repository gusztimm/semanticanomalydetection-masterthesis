import pickle
import os

import synthetic_evaluation
from evaluation.evaluation_result import precision, FullEvaluationResult
from evaluation.simple_log_collection import SimpleLogCollection
from knowledgebase.knowledgerecord import Observation

results_file = "/Users/han/git/semanticanomalydetection/results/raw_results/simmode_SimMode.SEMANTICSIMsimthres_0.7matchone_Truekbheuristics_True.ser"


def analyze_max_anomaly_occurrences(results: FullEvaluationResult):
    thresholds = [1, 5, 10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

    for threshold in thresholds:
        tp, fp = results.count_total_tp_and_fp(unique=True, obs_type=None, max_count=threshold)
        print("Threshold: " + str(threshold) + ", Precision (unique)", precision(tp, fp), "(", tp, "out of", tp + fp, ")")


def combine_freq_and_semantics(log_collection : SimpleLogCollection, results: FullEvaluationResult, obs_type = None):
    total_tp = 0
    total_fp = 0
    total_tpf = 0
    total_fpf = 0
    for log_name in log_collection.get_log_names():
        threshold = log_collection.get_log(log_name).total_traces() * 0.05
        log_result = results.log_result_map[log_name.split('.')[0]]
        tpf, fpf = log_result.tp_and_fp(unique=True, obs_type=obs_type, max_count=threshold)
        tp, fp = log_result.tp_and_fp(unique=True, obs_type=obs_type)
        total_tpf += tpf
        total_fpf += fpf
        total_tp += tp
        total_fp += fp
    # print(f'{obs_type} original tp {total_tp} fp {total_fp} precision {precision(total_tp, total_fp)}')
    print(f'{obs_type} filtered tp {total_tpf} fp {total_fpf} precision {precision(total_tpf, total_fpf)}')

# apply threshold and record tp + fp
# return results, should give insights into how both approaches can be combined
# results should be at variant level and for specific things

result = pickle.load(open(results_file, 'rb'))
print(os.getcwd())
noisy_log_collection = pickle.load(open("../" + synthetic_evaluation.noisy_log_collection_file, "rb"))

types = [None, Observation.XOR, Observation.ORDER, Observation.CO_OCC]
for obs_type in types:
    combine_freq_and_semantics(noisy_log_collection, result, obs_type)


# analyze_max_anomaly_occurrences(result)