import random
import os
import time
from datetime import datetime
import csv
import warnings
import pickle
from pm4py.objects.log.importer.xes import importer as xes_importer
from anomalydetection.anomalydetector import AnomalyDetector
from anomalydetection.configuration import Configuration
from knowledgebase.similaritycomputer import SimMode, SimilarityComputer, SemanticSimilarityComputer, \
    SynonymSimilarityComputer
from labelparser.bertparser.bert_tagger import BertTagger
from evaluation.evaluation_result import result_header, LogEvaluationResults, FullEvaluationResult
import evaluation.anomalyverifier as verifier
import knowledgebase_population.knowledgebasehandler as kb_handler

start_index = 0
end_index = 3000

load_serialized_similarities = True
load_simplified_log_collection = True

FOLDS_K = 10
REPS = 1

# noise insertion doesn't work when loading simplified log collections
LOG_SIZE = 1000
NOISY_TRACE_PROB = 0.7  # probability that noise will be inserted into a trace
NOISY_EVENT_PROB = 0.7  # probability that for a noisy trace there will be an additional noise insertion (repeats)

training_log_dir = "input/bpmai/training_logs"
log_dir = "input/bpmai/generated_logs"
noisy_log_dir = "input/bpmai/noisy_logs"

kb_ser_dir = "input/bpmai/extracted_records"
sim_comp_ser_file = "input/similarity/semanticsimcomputer.ser"

noisy_log_collection_file = os.path.join(noisy_log_dir, "simplifiedlogcollection.ser")
orig_log_collection_file = os.path.join(log_dir, "simplifiedlogcollection.ser")

# hide warnings from semantic similarity computation
warnings.filterwarnings("ignore", message="divide by zero encountered in true_divide")
warnings.filterwarnings("ignore", message="invalid value encountered in multiply")


def run_crossvalidation():
    configs = [
        #Configuration(sim_mode=SimMode.EQUAL),
        Configuration(sim_mode=SimMode.EQUAL, filter_heuristics_cscore=True),
        #Configuration(sim_mode=SimMode.EQUAL, kb_heuristics=True),
        #Configuration(sim_mode=SimMode.EQUAL, split_loops=True, limit_bos=True),
        #Configuration(sim_mode=SimMode.EQUAL, kb_heuristics=True, split_loops=True, limit_bos=True),
        #Configuration(sim_mode=SimMode.SYNONYM),
        #Configuration(sim_mode=SimMode.SYNONYM, filter_heuristics_cscore=True),
        #Configuration(sim_mode=SimMode.SYNONYM, split_loops=True, limit_bos=True),
        #Configuration(sim_mode=SimMode.SYNONYM, kb_heuristics=True),
        #Configuration(sim_mode=SimMode.SYNONYM, match_one=True, limit_bos=True),
        #Configuration(sim_mode=SimMode.SYNONYM, match_one=True, kb_heuristics=True, limit_bos=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.7),
        Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.7, filter_heuristics_cscore=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.7, split_loops=True, limit_bos=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.7, kb_heuristics=True, limit_bos=False),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.7, kb_heuristics=True, match_one=True, limit_bos=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.5),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.5, filter_heuristics_cscore=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.5, kb_heuristics=True, match_one=True, limit_bos=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.6, limit_bos=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.6, kb_heuristics=True, limit_bos=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.8, limit_bos=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.8, kb_heuristics=True, limit_bos=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.9, limit_bos=True),
        #Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.9, kb_heuristics=True, limit_bos=True),
    ]

    results_file = "output/results_vo_cn_at_fixconflTest_" + time.strftime("%Y%m%d%H%M%S") + ".csv"
    orig_log_collection = pickle.load(open(orig_log_collection_file, "rb"))
    noisy_log_collection = pickle.load(open(noisy_log_collection_file, "rb"))

    with open(results_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        header = result_header
        writer.writerow(header)

        log_names = extract_log_names(log_dir)[start_index:end_index]
        for config in configs:
            parser = load_parser(config.use_bert_parser)
            #Load sim computer
            sim_computer = load_sim_computer(config, parser, log_names)
            all_config_results = []
            for rep in range(REPS):
                rep_results = FullEvaluationResult(config, rep)
                chunks = list(split_into_chunks(log_names, FOLDS_K))
                start_time = datetime.now()
                for fold in range(len(chunks)):
                    test_chunk = chunks[fold]
                    fold_str = "config: " + str(configs.index(config) + 1) + " rep: " + str(rep + 1) + " fold: " + \
                               str(fold + 1)
                    print("Starting", fold_str)
                    train_logs = [item for chunk in chunks if chunk != test_chunk for item in chunk]
                    kb = kb_handler.populate_from_ser_fragments(kb_ser_dir, train_logs)
                    kb.min_support = config.min_support
                    kb.apply_filter_heuristics = config.use_kb_heuristics
                    kb.filter_heuristics_rank = config.filter_heuristics_rank
                    kb.filter_heuristics_cscore = config.filter_heuristics_cscore
                    for log_name in test_chunk:
                        print(fold_str, "log:", log_name, "nr", test_chunk.index(log_name) + 1, "out of",
                              len(test_chunk))
                        log_result = evaluate_on_simple_log(kb, config, parser, sim_computer, log_name,
                                                            orig_log_collection.get_log(log_name),
                                                            noisy_log_collection.get_log(log_name))
                        rep_results.add_log_result(log_name, log_result)
                end_time = datetime.now()
                rep_results.runtime = end_time - start_time
                print("\nConfig:", configs.index(config) + 1, "rep", rep + 1, "done.")
                all_config_results.append(rep_results)
                rep_results.print_results()
                writer.writerow(rep_results.to_array())
                save_full_eval_result(config, rep_results)
            if REPS > 1:
                write_aggregate_config_results(writer, config, all_config_results)
    print('\nEvaluation done')


def evaluate_on_simple_log(kb, config, parser, sim_computer, log_name, orig_simple_log, noisy_simple_log) -> LogEvaluationResults:
    # detect anomalies
    detector = AnomalyDetector(kb, config, parser, sim_computer,
                               noisy_simple_log, log_name, "simplified_log", already_simplified=True)
    detected_anomalies = detector.detect_anomalies()
    detected_variants = detector.anomalous_variants

    # record anomaly and trace-level correctness
    log_result = LogEvaluationResults()
    log_result.true_anomalies, log_result.false_anomalies = verifier.analyze_anomaly_correctness(config,
                                                                                                 detected_anomalies,
                                                                                                 orig_simple_log)

    log_result.trace_results = verifier.analyze_trace_accuracy(detected_variants, orig_simple_log, noisy_simple_log)
    return log_result


def split_into_chunks(data, folds):
    ys = list(data)
    random.shuffle(ys)
    size = len(ys) // folds
    leftovers = ys[size * folds:]
    for c in range(folds):
        if leftovers:
            extra = [leftovers.pop()]
        else:
            extra = []
        yield ys[c * size:(c + 1) * size] + extra


def extract_log_names(directory):
    return [os.path.basename(filepath).split(".")[0] for filepath in os.listdir(directory)
            if filepath.endswith(".xes") or filepath.endswith(".xes.xml")]


def _initialize_similarity_matrix(sim_computer, log_names, parser):
    print("initializing semantic similarity matrix for entire data collection")
    log_actions = _collect_all_log_actions(log_names, parser)
    verbocean_actions = kb_handler.linguisticpopulator.get_all_verbs()
    kb_verbs, dictionary, docsim_index = sim_computer.initialize_similarities(
        kb_verbs=log_actions.union(verbocean_actions), log_verbs=log_actions)
    pickle.dump((kb_verbs, dictionary, docsim_index), open(sim_comp_ser_file, "wb"))
    print("finished populating semantic similarity matrix")


def _load_serialized_similarity_matrix(sim_computer):
    kb_verbs, dictionary, docsim_index = pickle.load(open(sim_comp_ser_file, "rb"))
    sim_computer.set_loaded_similarities(kb_verbs, dictionary, docsim_index)


def _collect_all_log_actions(log_names, parser):
    all_actions = set()
    for log_name in log_names:
        log_file = os.path.join(log_dir, log_name + ".xes")
        log = xes_importer.apply(log_file)
        log_actions = {parser.get_action(event["concept:name"]) for trace in log for event in trace}
        all_actions = all_actions.union(log_actions)
    if None in all_actions:
        all_actions.remove(None)
    print(len(all_actions), "found in considered logs")
    return all_actions


def write_aggregate_config_results(writer, config, all_config_results):
    row = [str(config), 'avg.']
    for i in range(2, len(all_config_results[0].to_array())):
        avg_i = sum([rep_result.to_array()[i] for rep_result in all_config_results]) / len(all_config_results)
        row.append(avg_i)
    writer.writerow(row)


def load_parser(use_bert_parser=True):
    if use_bert_parser:
        return BertTagger()
    else:
        # hmm_parser.train_parser(hmm_parser.PARSER_PATH)
        return hmm_parser.load_default_parser()


def load_sim_computer(config, parser, log_names):
    if config.sim_mode == SimMode.EQUAL:
        return SimilarityComputer()
    if config.sim_mode == SimMode.SYNONYM:
        return SynonymSimilarityComputer(match_one=config.match_one)
    if config.sim_mode == SimMode.SEMANTIC_SIM:
        sim_computer = SemanticSimilarityComputer(match_one=config.match_one,
                                                  sim_threshold=config.sim_threshold,
                                                  compute_sim_per_log=False)
        if load_serialized_similarities:
            _load_serialized_similarity_matrix(sim_computer)
        else:
            _initialize_similarity_matrix(sim_computer, log_names, parser)
        return sim_computer
    return None


def save_full_eval_result(config, evaluation_result):
    folder = "output/raw_results/"
    if not os.path.exists(folder):
        os.makedirs(folder)
    out_file = folder + config.tofilename() + ".ser"
    pickle.dump(evaluation_result, open(out_file, "wb"))


if __name__ == "__main__":
    run_crossvalidation()
