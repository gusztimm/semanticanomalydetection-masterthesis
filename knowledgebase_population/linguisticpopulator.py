from sklearn import datasets
from knowledgebase.knowledgebase import KnowledgeBase
from knowledgebase.knowledgerecord import Observation, Dataset
from sklearn.preprocessing import minmax_scale, StandardScaler

import pickle

"""
@author: Gusztáv Megyesi
"""


rel_to_observation = {#VerbOcean
                      "antonymy": Observation.XOR,
                      "opposite-of": Observation.XOR,
                      "can-result-in": Observation.CO_OCC,
                      "happens-before": Observation.ORDER,
                      #ConceptNet
                      "Antonym": Observation.XOR,
                      "HasPrerequisite": Observation.ORDER,
                      #Atomic
                      "xNeed" : Observation.ORDER, #Before, PersonX needed -> ORDER (like HasPrerequisite)
                      "xWant": Observation.CO_OCC, #As a result, PersonX wants -> ENABLEMENT
                      "xIntent": Observation.CO_OCC, #Because PersonX wanted -> ENABLEMENT
                      "xEffect": Observation.CO_OCC, #PersonX then -> ENABLEMENT
                      #"isBefore": Observation.ORDER, #happens before -> ORDER - manually set to ISAFTER to retain order
                      "isAfter": Observation.ORDER #happens after -> ORDER)
                    }


def populate(knowledge_base, count_per_record = 1):

    candidates = set()

    # PART 1: Load VerbOcean records
    verbocean_path = "input/verbocean.txt"
    input_file = verbocean_path

    # Parses csv and stores content in knowledge base
    with open(input_file) as f:
        line = f.readline()
        while line:
            if not line.startswith("#"):
                (verb1, rel, verb2, conf) = _line_to_tuple_verbocean(line)
                if rel in rel_to_observation:
                    observation_type = rel_to_observation[rel]
                    candidates.add((verb1, verb2, observation_type, '', Dataset.VERBOCEAN, conf)) #empty string is object string
            line = f.readline()


    print('finished populating based on VerbOcean')
    print(f'candidates length with only VO: {len(candidates)}')

    # PART 2: Load Conceptnet records
    with open('/home/gumegyes/semanticanomalydetection/semanticanomalydetection-masterthesis/knowledgebase_population/additional_kb/kb_conceptnet.ser','rb') as pickle_loader:
        kb_conceptnet = pickle.load(pickle_loader)

    for record in kb_conceptnet:
        # verbs must not be the same
        if record['verb1']!=record['verb2']:

            # make tuple
            record_tuple = _line_to_tuple_serialized(record, 'conceptnet')
            verb1 = _list_to_string(record_tuple[0])
            verb2 = _list_to_string(record_tuple[2])
            obj = _list_to_string(record_tuple[3])
            rel = record_tuple[1]
            score = record_tuple[4]

            observation_type = rel_to_observation[rel]

            # if exists, leave it
            if (verb1, verb2, observation_type, '', Dataset.CONCEPTNET, score) not in candidates:
                #print('signal: candidate does NOT exist yet, proceed to check further')

                if observation_type==Observation.XOR: #relation: Antonym
                    #print('signal: candidate is ANTONYM, proceed to check if exists opposite way')
                
                    # if opposite relation already exists, skip
                    # note: if opposite is there with another score/dataset, it will be filtered in kb.add_observation()
                    if (verb2, verb1, observation_type, '', Dataset.CONCEPTNET, score) not in candidates:
                        #print('signal: candidate is ANTONYM, and not in dict yet, add it!')
                        candidates.add((verb1, verb2, observation_type, '', Dataset.CONCEPTNET, score))
                        
                        # set counter
                        #counter_antonym+=1

                elif observation_type==Observation.ORDER: #relation: HasPrerequisite
                    #print('signal: candidate is ORDER, and not in dict yet, add it!')
                    #CAUTION:
                    # VerbOcean has relation: verb1 - HappensBefore - verb2
                    # ConceptNet has relation: verb1 - HasPrerequisite - verb2 // meaning that verb2 happensBefore verb1
                    candidates.add((verb2, verb1, observation_type, '', Dataset.CONCEPTNET, score))
                    # set counter
                    #counter_hasprerequisite+=1
            else:
                #print('signal: candidate EXISTS, skipping')
                pass


    print(f'candidate length with also CN: {len(candidates)}')
    print('finished populating based on ConceptNet')
    
    
    #PART 3: Load Atomic records
    with open('/home/gumegyes/semanticanomalydetection/semanticanomalydetection-masterthesis/knowledgebase_population/additional_kb/kb_atomic.ser','rb') as pickle_loader:
        kb_atomic = pickle.load(pickle_loader)


    for record in kb_atomic:
        # verbs must not be the same
        if record['verb1']!=record['verb2']:

            # make tuple
            record_tuple = _line_to_tuple_serialized(record, 'atomic')
            verb1 = _list_to_string(record_tuple[0])
            verb2 = _list_to_string(record_tuple[2])
            obj = _list_to_string(record_tuple[3])
            rel = record_tuple[1]
            score = record_tuple[4]

            observation_type = rel_to_observation[rel]

            # if exists, leave it
            if (verb1, verb2, observation_type, obj, Dataset.ATOMIC, score) not in candidates:
                #print('signal: candidate does NOT exist yet, proceed to check further')

                if observation_type==Observation.XOR: #relation: Antonym
                    #print('signal: candidate is ANTONYM, proceed to check if exists opposite way')

                    # if opposite relation already exists, skip
                    # note: if opposite is there with another score/dataset, it will be filtered in kb.add_observation()
                    if (verb2, verb1, observation_type, obj, Dataset.ATOMIC, score) not in candidates:
                        #print('signal: candidate is ANTONYM, and not in dict yet, add it!')
                        candidates.add((verb1, verb2, observation_type, obj, Dataset.ATOMIC, score))
                        
                        # set counter
                        #counter_antonym+=1

                elif observation_type==Observation.ORDER:
                    #print('signal: candidate is ORDER, and not in dict yet, add it!')
                    #CAUTION:
                    # VerbOcean has relation: verb1 - happensBefore - verb2
                    # ConceptNet has relation: verb1 - hasPrerequisite - verb2 // meaning that verb2 happensBefore verb1
                    candidates.add((verb2, verb1, observation_type, obj, Dataset.ATOMIC, score))
                    # set counter
                    #counter_hasprerequisite+=1
                elif observation_type==Observation.CO_OCC:
                    candidates.add((verb1, verb2, observation_type, obj, Dataset.ATOMIC, score))
            else:
                #print('signal: candidate EXISTS, skipping')
                pass

    print(f'candidate length with also Atomic: {len(candidates)}')
    print('finished populating based on Atomic')

    # PART 4: Filter false antonyms

    added = set()
    counter = 0

    # filter out false antonyms
    for (verb1, verb2, observation_type, obj, dataset, score) in candidates:
        knowledge_base.add_observation(verb1, verb2, obj, observation_type, dataset, score, count = count_per_record)
        continue
        #TODO remove continue

        if observation_type in (Observation.ORDER, Observation.CO_OCC):
            #print('adding ORDER/CO_OCC rel:', verb1, verb2)
            knowledge_base.add_observation(verb1, verb2, obj, observation_type, dataset, score, count = count_per_record)
            counter+=1

        if observation_type is Observation.XOR:
            
            # Is there for this antonym relation also an ORDER relation?
            xor_order_1 = [candidate for candidate in candidates if candidate[0]==verb1 and candidate[1]==verb2 and candidate[2]==Observation.ORDER]
            xor_order_2 = [candidate for candidate in candidates if candidate[0]==verb2 and candidate[1]==verb1 and candidate[2]==Observation.ORDER]

            if len(xor_order_1)==0 and len (xor_order_2)==0:
                if (verb2, verb1, observation_type, obj) not in added:
                    #print('adding ANTONYM rel:', verb1, verb2)
                    knowledge_base.add_observation(verb1, verb2, obj, observation_type, dataset, score, count = count_per_record)
                    counter+=1
                    added.add( (verb1, verb2, observation_type, obj))

            # The version below performs object-specific check:
            # e.g. does NOT recognize if [start cooking] vs. [end cooking] is antonym, but [start progress] vs. [end progress] is ORDER
            """
            if (verb1, verb2, Observation.ORDER) not in candidates and (
            verb2, verb1, Observation.ORDER) not in candidates:
                if (verb2, verb1, observation_type) not in added:
                    #print('adding ANTONYM rel:', verb1, verb2)
                    knowledge_base.add_observation(verb1, verb2, obj, observation_type, count = count_per_record)
                    counter+=1
                    added.add( (verb1, verb2, obj, observation_type))
            """
    
# PART 5: set normalized confidence scores in case a single record is available in several datasets
    knowledge_base.set_norm_confidence_for_all_records()


    print('finished populating based on linguistic resources')
            

def get_all_verbs():
    temp_kb = KnowledgeBase()
    populate(temp_kb)
    return temp_kb.get_all_verbs()


def _line_to_tuple_serialized(record, record_src):
    verb1 = record['verb1']
    verb2 = record['verb2']
    obj = record['object1'] #object1=object2 in extraction
    rel = record['relation']

    # Get raw confidence score - cap it at 1 (Conceptnet)
    if 'score' in record.keys(): # affects only conceptnet
        record_score = record['score']
        conf = float(record_score[record_score.find('::')+3:len(record_score)].strip())
        conf = min(1,conf)
    else: # affects Atomic
        conf = 1


    #Normalize confidence score
    #Note: we even min-max-normalize Atomic score here, but as long as it is flat-set to 1 by default, it will remain 1
    min_conf = 0.1
    max_conf = 1
    normconf = _normalize_conf(min_conf, max_conf, conf)

    # Invert isBefore
    if record_src=='atomic' and rel=='isBefore':
        return (verb2, 'isAfter', verb1, obj, normconf, record_src)
    else:
        return (verb1, rel, verb2, obj, normconf, record_src)


def _line_to_tuple_verbocean(line):
    start_br = line.find('[')
    end_br = line.find(']')
    conf_delim = line.find('::')
    verb1 = line[:start_br].strip()
    rel = line[start_br + 1: end_br].strip()
    verb2 = line[end_br + 1: conf_delim].strip()

    #Normalize confidence score
    min_conf = 8.502357
    max_conf = 26.451366
    conf = float(line[conf_delim+3: len(line)].strip())
    normconf = _normalize_conf(min_conf, max_conf, conf)

    return (verb1, rel, verb2, normconf)

def _list_to_string(list):
    for str in list:
        if str!='':
            return str
    else:
        return ''

def _normalize_conf(min_conf, max_conf, score):
    return (score-min_conf)/(max_conf-min_conf)

def get_all_verbs():
    temp_kb = KnowledgeBase()
    populate(temp_kb)
    return temp_kb.get_all_verbs()