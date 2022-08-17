"""
This file is part of the repository belonging to the Master Thesis of Gusztáv Megyesi - MN 1526252
Title: Incorporation of Commonsense Knowledge Resources for Semantic Anomaly Detection in Process Mining
Submitted to the Data and Web Science Group - Prof. Dr. Han van der Aa - University of Mannheim in August 2022
"""
import sys
import os
myDir = os.getcwd()
sys.path.append(myDir)

from labelparser import label_utils
from labelparser.bertparser.bert_tagger import BertTagger
from labelparser import label_utils
import pickle
import xml.etree.ElementTree as ET

xes_folder = 'input/bpmai/noisy_logs/'
list_output = 'knowledgebase_population/'

def get_events_from_xes(xes_file):

    extracted_phrases = set()

    tree = ET.parse(xes_file)
    root = tree.getroot()

    for trace in root:
        for event in trace:
            for element in event:
                if element.tag=='string':
                    if element.attrib['key']=='concept:name':
                        extracted_phrases.add(element.attrib['value'])
                    else:
                        continue
                else:
                    continue

    return extracted_phrases

def results_writeFile(extracted_phrases):
    with open(f'{list_output}xes_list.txt', 'a+') as xes_output:
        for record in extracted_phrases:
            xes_output.write(f'{label_utils.sanitize_label(record)}\n')

def run_collect_xes_activities():
    all_activities = set()
    counter = 0

    for xes_file in os.listdir(xes_folder):
        if not xes_file.endswith('.xes'):
            continue

        counter+=1

        xes_full_path = f'{xes_folder}{xes_file}'

        print(f'Reading file nr. {counter} - {xes_file}')

        xes_activities = get_events_from_xes(xes_full_path) #set

        for element in xes_activities:
            all_activities.add(element)

    results_writeFile(all_activities)

def serialize_xes_activities(xes_list_path):
    i=0
    parser = BertTagger()
    serialized_xes = []

    with open(xes_list_path) as xes_list:
        for event in xes_list:
            i+=1
            parsed_event = parser.parse_label(event)

            parsed_dict = {
                'xes_actions': [label_utils.lemmatize_word(action) for action in parsed_event.actions],
                'xes_bos' : parsed_event.bos
            }

            print(f"Serializing entry {i}: actions: {parsed_dict['xes_actions']} BO: {parsed_dict['xes_bos']}")
            serialized_xes.append(parsed_dict)

    with open('xes_serialized.ser','wb') as pickle_writer:
        pickle.dump(serialized_xes, pickle_writer)


if __name__ == '__main__':
    # 1.  - load up xes_list.txt with activities
    #run_collect_xes_activities()

    # 2.  - serialize each knowledge record
    #serialize_xes_activities('/home/gumegyes/semanticanomalydetection/semanticanomalydetection-masterthesis/knowledgebase_population/xes_list.txt')

    pass
