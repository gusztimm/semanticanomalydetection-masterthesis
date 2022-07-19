import os
import time
import csv
import warnings
import pickle
from pm4py.objects.log.importer.xes import importer as xes_importer
from anomalydetection.anomalydetector import AnomalyDetector
from anomalydetection.configuration import Configuration
from knowledgebase.similaritycomputer import SimMode, SimilarityComputer, SemanticSimilarityComputer, \
    SynonymSimilarityComputer
from labelparser.bertparser.bert_tagger import BertTagger
import knowledgebase_population.knowledgebasehandler as kb_handler

log_dir = "input/logs"
kb_ser = "input/serializedkbs/full_kb.ser"
kb_records_ser_dir = "input/bpmai/extracted_records"
sim_comp_ser_dir = "input/similarity/realworldloginstantiations"

# hide warnings from semantic similarity computation
warnings.filterwarnings("ignore", message="divide by zero encountered in true_divide")
warnings.filterwarnings("ignore", message="invalid value encountered in multiply")

event_key_map = {
    "BPI_2012.xes": "concept:name",
    "BPIC15_5.xes": "activityNameEN",
    "BPI_2018.xes": "concept:name",
}


def run_evaluation():
    configs = [
        Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.7, kb_heuristics=True, match_one=True, split_loops=True),
        # Configuration(sim_mode=SimMode.SEMANTIC_SIM, sim_threshold=0.5, kb_heuristics=True, split_loops=True),
    ]

    results_file = "output/results_realworld" + time.strftime("%Y%m%d%H%M%S") + ".csv"

    kb = obtain_knowledgebase(kb_ser)

    with open(results_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        result_header = ["config", "log", "anomaly type", "event1", "event2", "verb1", "verb2", "record_conf", "anomaly_count"]
        writer.writerow(result_header)
        parser = BertTagger()
        for log_name in event_key_map.keys():
            log_file = os.path.join(log_dir, log_name)
            event_key = event_key_map[log_name]
            if os.path.exists(log_file):
                log = xes_importer.apply(log_file)
                for config in configs:
                    # initialize configuration
                    kb.min_support = config.min_support
                    kb.apply_filter_heuristics = config.use_kb_heuristics
                    sim_computer = load_sim_computer(config, parser, log, log_name, event_key)

                    # detect anomalies
                    detector = AnomalyDetector(kb, config, parser, sim_computer, log, log_name, event_key, already_simplified=False)
                    anomaly_counter = detector.detect_anomalies()

                    # record results
                    print('\ndetected anomalies:')
                    for anomaly in anomaly_counter:
                        print(anomaly, ' count:', anomaly_counter[anomaly])
                        row = [config, log_name]
                        row.extend(anomaly.to_array())
                        row.append(anomaly_counter[anomaly])
                        writer.writerow(row)
    print('\nEvaluation done')


def obtain_knowledgebase(ser_file):
    #if os.path.exists(ser_file):
    if False:
        return kb_handler.load_serialized_kb(ser_file)
    else:
        kb = kb_handler.populate_from_ser_fragments(kb_records_ser_dir, add_verbocean=True)
        pickle.dump(kb, open(ser_file, "wb"))
        return kb


def load_sim_computer(config, parser, target_log, log_name, event_key):
    if config.sim_mode == SimMode.EQUAL:
        return SimilarityComputer()
    if config.sim_mode == SimMode.SYNONYM:
        return SynonymSimilarityComputer(match_one=config.match_one)
    if config.sim_mode == SimMode.SEMANTIC_SIM:
        sim_computer = SemanticSimilarityComputer(match_one=config.match_one,
                                                  sim_threshold=config.sim_threshold,
                                                  compute_sim_per_log=False)
        ser_file = os.path.join(sim_comp_ser_dir, log_name + ".ser")
        if os.path.exists(ser_file):
            _load_serialized_similarity_matrix(sim_computer, ser_file)
        else:
            _initialize_similarity_matrix(sim_computer, target_log, log_name, event_key, parser, ser_file)
        return sim_computer
    return None


def _initialize_similarity_matrix(sim_computer, target_log, log_name, event_key, parser, ser_file):
    print("initializing semantic similarity matrix for KB and target log")
    log_actions = _collect_actions_in_log(target_log, event_key, parser)
    verbocean_actions = kb_handler.linguisticpopulator.get_all_verbs()
    kb_verbs, dictionary, docsim_index = sim_computer.initialize_similarities(
        kb_verbs=log_actions.union(verbocean_actions), log_verbs=log_actions)
    pickle.dump((kb_verbs, dictionary, docsim_index), open(ser_file, "wb"))
    print("finished populating semantic similarity matrix")


def _load_serialized_similarity_matrix(sim_computer, ser_file):
    kb_verbs, dictionary, docsim_index = pickle.load(open(ser_file, "rb"))
    sim_computer.set_loaded_similarities(kb_verbs, dictionary, docsim_index)


def _collect_actions_in_log(log, event_key, parser):
    log_actions = {parser.get_action(event[event_key]) for trace in log for event in trace}
    if None in log_actions:
        log_actions.remove(None)
    return log_actions


if __name__ == "__main__":
    run_evaluation()
