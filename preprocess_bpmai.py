import os
import pickle
import gc
import signal
from conversion.jsontopetrinetconverter import JsonToPetriNetConverter
import conversion.petrinetanalysis as pna
import pm4py.objects.petri.check_soundness as soundness
from pm4py.objects.log.exporter.xes import factory as xes_exporter
from pm4py.objects.log.importer.xes import importer as xes_importer
from shutil import copy
import evaluation.log_simulator as simulator
import synthetic_evaluation

from knowledgebase_population.xespopulator import XESPopulator
from labelparser.bertparser.bert_tagger import BertTagger
from evaluation.simple_log_collection import SimpleLogCollection

# TODO: ref to path names from run_evaluation.py instead
json_dir = "input/knowledgebase/bpmai/models"
petri_dir = "input/knowledgebase/bpmai/petrinets_en"
# xes_dir = "input/knowledgebase/bpmai/generated_logs"
# # xes_dir_filtered = "input/knowledgebase/bpmai/generated_logs_filtered"
# xes_dir_training = "input/knowledgebase/bpmai/generated_logs_training"
# # xes_dir_training_filtered = "input/knowledgebase/bpmai/generated_logs_training_filtered"
# xes_dir_noisy = "input/knowledgebase/bpmai/noisy_logs"
# kr_dir = "input/knowledgebase/bpmai/extracted_records"

start_index = 0
end_index = 20000


def alarm_handler(signum, frame):
    raise Exception("timeout")


def generate_logs_from_petri_sers(timeout, target_dir, target_dir_no_loops):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    if not os.path.exists(target_dir_no_loops):
        os.makedirs(target_dir_no_loops)
    pnet_ser_files = [f for f in os.listdir(petri_dir) if f.endswith(".pnser")]
    pnet_ser_files.sort()
    pnet_ser_files = pnet_ser_files[start_index:end_index]
    print("Total number of pnet files:", len(pnet_ser_files))
    success = 0
    done = 0

    for ser_file in pnet_ser_files:
        print('Started parsing:', ser_file)
        case_name = os.path.basename(ser_file).split('.')[0]
        net, initial_marking, final_marking = pickle.load(open(os.path.join(petri_dir, ser_file), 'rb'))
        try:
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(timeout)
            is_relaxed_sound = soundness.check_relaxed_soundness_net_in_fin_marking(net, initial_marking,
                                                                                    final_marking)
        except Exception:
            print("WARNING: Time out during soudness checking.")
            signal.alarm(0)

        if is_relaxed_sound:
            print('model is sound. Generating traces')
            log, log_no_loops = pna.get_traces(net, initial_marking, final_marking, timeout, remove_loops=True,
                                 extensive=True)
            if len(log) > 0:
                xes_file = os.path.join(target_dir, case_name + ".xes")
                xes_exporter.export_log(log, xes_file)

                xes_file2 = os.path.join(target_dir_no_loops, case_name + ".xes")
                xes_exporter.export_log(log_no_loops, xes_file2)
                print(f"Saved as model {xes_file}")
                success += 1


        done += 1
        print(f"Number of converted (sound) models: {success} / {done}")
        if done % 25 == 0:
            gc.collect()
    print("Run completed.")


def convert_jsons_to_petri():
    converter = JsonToPetriNetConverter()
    json_files = [f for f in os.listdir(json_dir) if f.endswith(".json") and not f.endswith("meta.json")]
    json_files.sort()
    print("Total number of json files:", len(json_files))
    success = 0
    failed = 0

    if not os.path.exists(petri_dir):
        os.makedirs(petri_dir)

    for json_file in json_files:
        case_name = os.path.basename(json_file).split('.')[0]
        try:
            # Load and convert json-based BPMN into Petri net
            net, initial_marking, final_marking = converter.convert_to_petri_net(
                os.path.join(json_dir, json_file))
            pnet_file = os.path.join(petri_dir, case_name + ".pnser")
            pickle.dump((net, initial_marking, final_marking), open(pnet_file, 'wb'))
            success += 1
        except:
            print("WARNING: Error during conversion from bpmn to Petri net.")
            failed += 1
        print(success + failed, "jsons done. Succes: ", success, "failed: ", failed)
        if (success + failed) % 50 == 0:
            gc.collect()
    print("Run completed.")


def extract_knowledge_records_from_xes_files(log_dir):
    kr_dir = synthetic_evaluation.kb_ser_dir
    if not os.path.exists(kr_dir):
        os.makedirs(kr_dir)
    log_files = [f for f in os.listdir(log_dir) if f.endswith(".xes")]
    log_files.sort()
    log_files = log_files[start_index:end_index]
    print("Total number of xes files:", len(log_files))
    populator = XESPopulator(BertTagger())

    with_observations = 0
    done = 0
    for log_file in log_files:
        log = xes_importer.apply(os.path.join(log_dir, log_file))
        case_name = os.path.basename(log_file).split('.')[0]
        observations = populator.extract_records_from_log(log)
        ser_file = os.path.join(kr_dir, case_name + ".krser")
        pickle.dump(observations, open(ser_file, 'wb'))
        print("Stored", len(observations), "observations")
        if observations:
            with_observations += 1
        done += 1
        print(done, "done.", with_observations, "logs contributing to records")
        if done % 25 == 0:
            gc.collect()
    print("Run completed")


def keep_only_english_files(input_dir, output_dir, file_extension):
    txt = "input/knowledgebase/bpmai/english_models.txt"
    with open(txt, 'r') as f:
        lines = f.read().splitlines()
        names = [line.split('.')[0] for line in lines]
        all_files = [f for f in os.listdir(input_dir) if f.endswith(file_extension)]
        en_files = [f for f in all_files if os.path.basename(f).split('.')[0] in names]
        for en_file in en_files:
            copy(os.path.join(input_dir, en_file), output_dir)


def remove_pointless_cases(input_dir, target_dir):
    #     removes all processes for which there are no two event classes with the same object
    #     -> will never lead to an anomaly in any case
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    log_files = [f for f in os.listdir(input_dir) if f.endswith(".xes")]
    retained_files = []
    log_files.sort()
    log_files = log_files[start_index:end_index]
    parser = BertTagger()
    for log_file in log_files:
        if not _is_pointless(input_dir, log_file, parser):
            copy(os.path.join(input_dir, log_file), target_dir)
            retained_files.append(log_file)
    print(len(retained_files), " files kept from", len(log_files), "total.")


def _is_pointless(log_dir, log_file, parser):
    log = xes_importer.apply(os.path.join(log_dir, log_file))
    seen_classes = set()
    log_objects = set()
    for trace in log:
        for event in trace:
            event_class = event["concept:name"]
            # check if class has not yet been seen
            if not event_class in seen_classes:
                seen_classes.add(event_class)
                event_objects = parser.parse_label(event_class).bos
                # check if any object has already been seen
                if bool(set(event_objects) & log_objects):
                    return False
                log_objects.update(event_objects)
    return True


def save_noisy_logs(input_dir, target_dir, noisy_trace_prob, noisy_event_prob, log_size):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    log_files = [f for f in os.listdir(input_dir) if f.endswith(".xes")]
    for log_file in log_files:
        log = xes_importer.apply(os.path.join(input_dir, log_file))
        noisy_log = simulator.insert_noise(log, noisy_trace_prob, noisy_event_prob, log_size)
        noisy_xes_file = os.path.join(target_dir, log_file)
        xes_exporter.export_log(noisy_log, noisy_xes_file)
        print(f"Saved as model {noisy_xes_file}")
    print('done.')


def store_as_simple_log_collection(log_folder, out_file):
    log_files = [f for f in os.listdir(log_folder) if f.endswith(".xes")]
    out_file = os.path.join(log_folder, out_file)
    simple_log_collection = SimpleLogCollection()
    for log_file in log_files:
        log = xes_importer.apply(os.path.join(log_folder, log_file))
        simple_log_collection.add_log(log_file, log)
        if len(simple_log_collection.log_map) % 100 == 0:
            print(str(len(simple_log_collection.log_map)) + " logs done.")
            gc.collect()
    pickle.dump(simple_log_collection, open(out_file, 'wb'))
    print("All done.")


# convert_jsons_to_petri()
# keep_only_english_files(input_dir=petri_dir, output_dir="input/knowledgebase/bpmai/petrinets_en/", file_extension=".pnser")
# generate_logs_from_petri_sers(timeout=30, target_dir=xes_dir, target_dir_no_loops=xes_dir_training)
# remove_pointless_cases(input_dir=xes_dir, target_dir=xes_dir_filtered)
# remove_pointless_cases(input_dir=xes_dir_training, target_dir=xes_dir_training_filtered)
# extract_knowledge_records_from_xes_files(xes_dir_training)
# store_as_simple_log_collection(xes_dir_filtered, "simplifiedlogcollection.ser")
# save_noisy_logs(input_dir=xes_dir_filtered, target_dir=xes_dir_noisy,
#                 noisy_trace_prob=run_evaluation.NOISY_TRACE_PROB,
#                 noisy_event_prob=run_evaluation.NOISY_EVENT_PROB,
#                 log_size=run_evaluation.LOG_SIZE)
# store_as_simple_log_collection(xes_dir_noisy, "simplifiedlogcollection.ser")
