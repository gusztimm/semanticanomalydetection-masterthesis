"""
@author: Gusztáv Megyesi
"""

import sys
import os
myDir = os.getcwd()
sys.path.append(myDir)

import pickle
from labelparser.bertparser.bert_tagger import BertTagger
from labelparser import label_utils


class Atomic_Extractor:

    interesting_relations = {
        'xNeed', #Because PersonX needed -> ORDER
        'xWant', #As a result, PersonX wants -> ENABLEMENT
        'xIntent', #Because PersonX wanted -> ENABLEMENT
        'xEffect', #PersonX then -> ENABLEMENT
        'isBefore', #happens before -> ORDER
        'isAfter' #happens after -> ORDER)
    }

    paths = [
        'input/kb_atomic/train.tsv',
        'input/kb_atomic/test.tsv',
        'input/kb_atomic/dev.tsv'
    ]

    test_paths = [
        'input/kb_atomic/dev.tsv'
    ]

    def __init__(self):
        self.results = []

    def __repr__(self):
        return f'<Atomic Crawler with phrase_list of length {len(self.phrase_list)} and relations {self.interesting_relations}>'

    def add_record(self, record):
        self.results.append(record)

    def load_rawfile(self):
        parser = BertTagger()
        i=0

        for path in self.paths:
            with open(path) as rawfile:
                for line in rawfile:
                    line = line.replace("'s","")
                    line = line.replace("'d","")
                    line = line.replace('PersonX','')
                    line = line.replace('PersonY','')
                    line = line.replace('Person X','')
                    line = line.replace('Person Y','')
                    line = line.replace(' X ',' ')
                    line = line.replace(' Y ',' ')

                    line_list = line.split('\t')

                    relation = (line_list[1].strip())
                    statement1 = label_utils.remove_stopwords(line_list[0])
                    statement2 = label_utils.remove_stopwords(line_list[2])

                    if relation in self.interesting_relations:

                        # skip none-statements
                        if statement1== 'none' or statement2 == 'none':
                            continue

                        statement1_parsed = parser.parse_label(statement1)
                        statement2_parsed = parser.parse_label(statement2)

                        record = {
                            'verb1': [label_utils.lemmatize_word(action) for action in statement1_parsed.actions],
                            'object1' : statement1_parsed.bos,
                            'verb2' : [label_utils.lemmatize_word(action) for action in statement2_parsed.actions],
                            'object2' : statement2_parsed.bos,
                            'relation' : relation
                        }

                        if not (
                                (record['object1']==record['object2']) or
                                ('___' in record['object1']) or
                                ('___' in record['object2'])
                                ):
                            continue

                        self.add_record(record)
                        print(f'{relation} - {statement1} - {statement2}')

                    else:
                        continue

    def save_serialized_dict(self):
        with open('kb_atomic.ser','wb') as pickle_writer:
            pickle.dump(self.results,pickle_writer)

    def print_records(self):
        for result in self.results:
            print(f"{result['verb1']} {result['object1']} {result['relation']} {result['verb2']} {result['object2']}")



crawler = Atomic_Extractor()
crawler.load_rawfile()
crawler.save_serialized_dict()
