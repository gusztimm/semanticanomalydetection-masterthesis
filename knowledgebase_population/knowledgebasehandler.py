import os, pickle

from knowledgebase.knowledgebase import KnowledgeBase
from knowledgebase_population import linguisticpopulator
from knowledgebase.knowledgerecord import Dataset


bpm_ai_json_dir = "input/bpmai/models"
bpm_ai_petri_dir = "input/bpmai/petrinets"
bpm_ai_xes_dir = "input/bpmai/extracted_logs"
bpm_ai_ser_kr_dir = "input/bpmai/extracted_records"


def populate_knowledge_base(use_bpmai, use_verbocean):
    kb = KnowledgeBase()

    if use_bpmai:
        log_names = [os.path.basename(filepath) for filepath in os.listdir(bpm_ai_xes_dir) if filepath.endswith(".xes")]
        kb = populate_from_ser_fragments(bpm_ai_xes_dir, log_names, add_verbocean=False)

    if use_verbocean:
        # from verbocean records
        linguisticpopulator.populate(kb, count_per_record=1000)
    return kb


def load_serialized_kb(kb_file):
    kb = pickle.load(open(kb_file, "rb"))
    print("loaded knowledge base from", kb_file, "with", kb.get_record_numbers(), "records")
    return kb


def populate_from_ser_fragments(ser_dir, case_names=None, add_verbocean=True):
    print(f'ser_dir: {ser_dir}')
    kb = KnowledgeBase()
    # if case_names is not specified, all files will be used for population
    if not case_names:
        case_names = [f for f in os.listdir(ser_dir) if f.endswith(".krser")]
    for case_name in case_names:
        file_path = os.path.join(ser_dir, case_name)  #+ '.krser'
        print(file_path)
        if os.path.isfile(file_path):
            observations = pickle.load(open(file_path, "rb"))
            for observation in observations:
                kb.add_observation(observation[0], observation[1], '', observation[2], Dataset.BPMAI, 0) #empty string is object

    if add_verbocean:
        linguisticpopulator.populate(kb, count_per_record=1000)
    print("loaded kb with", kb.get_record_numbers(), "records")
    return kb

def populate_verbocean():
    kb = KnowledgeBase()
    linguisticpopulator.populate(kb, count_per_record=1000)
    print("loaded kb with", kb.get_record_numbers(), "records")
    return kb


