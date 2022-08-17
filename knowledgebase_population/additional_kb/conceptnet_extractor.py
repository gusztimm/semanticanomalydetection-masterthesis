"""
@author: Gusztáv Megyesi
"""
import os
import sys

myDir = os.getcwd()
sys.path.append(myDir)

from knowledgebase_population.conceptnet_crawler import ConceptNet_Crawler
from labelparser.bertparser.bert_tagger import BertTagger
from labelparser import label_utils
from knowledgebase.similaritycomputer import SynonymSimilarityComputer

class ConceptNet_Extractor:

    def extract_conceptnet():

        # load xes_list.txt
        xes_list = 'knowledgebase_population/xes_list.txt'

        # initialize verb_list
        verb_list = set()

        # initialize history
        verb_history = set()

        # load BERT-Tagger
        parser = BertTagger()

        # load ConceptNet crawler
        crawler = ConceptNet_Crawler()

        # load SynonymSimilarityComputer object for synonym retrieval
        sc = SynonymSimilarityComputer()

        # init counter
        counter = 0

        with open(xes_list) as xes_list:
            for line in xes_list:

                counter+=1
                print(f'Line {counter}: {line}')

                # BERT-tag phrases
                label = label_utils.remove_stopwords(line)
                ParsedLabel = parser.parse_label(label)
                actions = ParsedLabel.actions

                # Add verbs to verb_list (unique)
                for action in actions:
                    verb_list.add(action)

                #print(ParsedLabel.tags)
                #print(ParsedLabel.bos)
                #print(ParsedLabel.actions)

                # parse the list of verbs and find synonyms, put them into list
                for action in actions:
                    synonym_list = sc.get_synonyms(action)

                for synonym in synonym_list:
                    verb_list.add(synonym)

                print(f'Synonyms list of action array: {actions}: {synonym_list}')

                # iterate through list of verbs and use ConceptNet crawler

                # Execute ConceptNet Crawler
                for verb in verb_list:
                    if verb not in verb_history:
                        crawler.set_uri(verb)
                        crawler.run_query()
                        crawler.json_buildrelations()
                        crawler.results_writeFile()
                        crawler.reset()

                # add all verbs in this round to history so that they are not queried anymore
                for verb in verb_list:
                    verb_history.add(verb)

                # and write to file in case program breaks
                with open('ConceptNet_Verb_History.txt', 'a+') as vh_output:
                    for verb in verb_history:
                        vh_output.write(f'{verb}\n')

                # Reset verb_list
                verb_list = set()


if __name__ == '__main__':
    extractor = ConceptNet_Extractor()
    extractor.extract_conceptnet()
