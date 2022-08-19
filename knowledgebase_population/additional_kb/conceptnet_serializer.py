"""
This file is part of the repository belonging to the Master Thesis of Gusztáv Megyesi - MN 1526252
Title: Incorporation of Commonsense Knowledge Resources for Semantic Anomaly Detection in Process Mining
Submitted to the Data and Web Science Group - Prof. Dr. Han van der Aa - University of Mannheim in August 2022
"""


import sys
import os
myDir = os.getcwd()
sys.path.append(myDir)

import pickle
from labelparser.bertparser.bert_tagger import BertTagger
from labelparser import label_utils


class ConceptNet_Serializer:

    def __init__(self):
        self.results = []

    def __repr__(self):
        return f'<ConceptNet Serializer with serialized entries of length {len(self.results)}>'

    def add_record(self, record):
        self.results.append(record)

    # Function that cleans each line and puts each statement/relation into dict-format
    def conceptnet_tag_line(self, line):
        start_br = line.find('[')
        end_br = line.find(']')
        conf_delim = line.find('::')

        statement1 = line[:start_br].strip()
        rel = line[start_br + 1: end_br].strip()
        statement2 = line[end_br + 1: conf_delim].strip()
        score = line[conf_delim: len(line)].strip()

        return {'statement1' : statement1,
                'statement2' : statement2,
                'relation' : rel,
                'score' : score
                }


    # Function that loads CN-extraction output file, iterates through each line and extracts actions/objects/relations and confidence score
    def load_rawfile(self):
        parser = BertTagger()
        i=0

        with open('knowledgebase_population/additional_kb/ConceptNet_Output.txt') as rawfile:
            for line in rawfile:
                i+=1

                line_list = self.conceptnet_tag_line(line)

                relation = (line_list['relation'].strip())
                statement1 = label_utils.remove_stopwords(line_list['statement1'])
                statement2 = label_utils.remove_stopwords(line_list['statement2'])

                statement1_parsed = parser.parse_label(statement1)
                statement2_parsed = parser.parse_label(statement2)

                record = {
                    'verb1': [label_utils.lemmatize_word(action) for action in statement1_parsed.actions],
                    'object1' : statement1_parsed.bos,
                    'verb2' : [label_utils.lemmatize_word(action) for action in statement2_parsed.actions],
                    'object2' : statement2_parsed.bos,
                    'relation' : relation,
                    'score' : line_list['score']
                }

                # Only extract records, which:
                #- share the same object1
                #- have no object associated
                #- have a verb in both statements
                if not (
                        (
                        (record['object1']==record['object2']) or
                        (len(record['object1'])==0 and len(record['object2'])==0)
                        )
                        and
                        (
                        (len(record['verb1'])>0) and
                        (len(record['verb2'])>0)
                        )
                        ):
                    print(f"{i} - SKIPPED: verb1: {record['verb1']} - object1: {record['object1']} *{relation}* verb2: {record['verb2']} - object2: {record['object2']}")
                    continue

                self.add_record(record)
                print(f"{i} - ADDED: verb1: {record['verb1']} - object1: {record['object1']} *{relation}* verb2: {record['verb2']} - object2: {record['object2']}")

    def save_serialized_dict(self):
        with open('kb_conceptnet.ser','wb') as pickle_writer:
            pickle.dump(self.results,pickle_writer)

    def print_records(self):
        for result in self.results:
            print(f"{result['verb1']} {result['object1']} {result['relation']} {result['verb2']} {result['object2']}")



crawler = ConceptNet_Serializer()
crawler.load_rawfile()
crawler.save_serialized_dict()
