"""
@author: Gusztáv Megyesi
"""

import requests
import time

class ConceptNet_Crawler:

    # Relations that will be extracted from ConceptNet
    interesting_relations = {
        'HasPrerequisite',
        'Antonym'
    }
    
    # Offset: start from which result?
    # Limit: show this many results on one page
    def __init__(self, searchterm=None, offset=0, limit=1200):
        self.api_address = 'http://api.conceptnet.io'
        self.api_offset = offset
        self.api_limit = limit
        self.json_list = []
        self.results = []

        if (searchterm is not None):
             self.api_uri = '/c/en/' + searchterm
       
    def __repr__(self):
        return f'<ConceptNet Crawler with JSON of length {len(self.json_list)} - Last URI {self.api_uri}>'

    def reset(self):
        self.api_offset=0
        self.json_list = []
        self.results = []

    def set_uri(self, searchterm):
        self.api_uri = '/c/en/' + searchterm

    # Query URL is built from object properties and returned as string
    def prepare_query(self):
        return self.api_address + self.api_uri + '?offset=' + str(self.api_offset) + '&limit=' + str(self.api_limit)

    # Query URL is posted
    # If JSON is valid (i.e. there are results), then it is appended to the JSON list of this object
    # If JSON is paginated, then method is repeated and all JSON pages are retrieved
    def run_query(self):
        query = self.prepare_query()
        print(f'Query: {query}')

        # ConceptNet API allows 3600 requests per hour = 1 request/second
        time.sleep(1)

        # Handle case if internet connection is interrupted
        while True:
            got_json = False
            try:
                api_json = requests.get(query).json()
                got_json = True
            except:
                print("Connection refused or no Internet - retrying in 5 seconds...")
                time.sleep(5)
            finally:
                if got_json:
                    break

        if (self.json_isValid(api_json)):
            self.json_list.append(api_json)

        while self.has_nextPage(api_json):
            self.api_offset+=self.api_limit
            self.run_query()
            break

    # Gets URL of next page of JSON
    def get_nextPage(self, json):
        return self.api_address + json['view']['nextPage']

    # Checks JSON if there is a next page
    @staticmethod
    def has_nextPage(json):
        return (
            ('view' in json.keys()) 
        and ('@type' in json['view'].keys())
        and (json['view']['@type']=="PartialCollectionView")
        and ('nextPage' in json['view'].keys())
        )

    # JSON is valid and contains results if there is no 'error' attribute
    @staticmethod
    def json_isValid(json):
        return ('error' not in json.keys())

    # This function parses all JSONs that have been retrieved previously
    # The relations are built and stored in the result list, where each result is a dict of nodes/relations
    def json_buildrelations(self):
        for json in self.json_list:
            for edge in json['edges']:

                # Check if format is fine - e.g. for external relations, extraction won't work
                # all() checks if all of the keys below exist
                # if yes, then JSON content is mapped to variables
                if all(
                    [all([edge_key in edge.keys() for edge_key in ['rel', 'start', 'end', 'weight']]),
                    all([start_key in edge['start'].keys() for start_key in ['label', 'language']]),
                    all([start_key in edge['end'].keys() for start_key in ['label', 'language']])]
                ):
                    e_Weight = edge['weight']
                    e_Relation = edge['rel']['label']
                    e_Start_Label = edge['start']['label']
                    e_Start_Lang = edge['start']['language']
                    e_End_Lang = edge['end']['language']
                    e_End_Label = edge['end']['label']
                # If format of this relation is not okay, then skip to next relation
                else:
                    continue
                
                # If the relation is 'interesting' and both nodes are in English, then retrieve record
                if e_Relation in self.interesting_relations and e_Start_Lang == 'en' and e_End_Lang == 'en':
                    record = {
                        'start' : e_Start_Label,
                        'end' : e_End_Label,
                        'relation' : e_Relation,
                        'weight' : e_Weight
                    }
                    # Append record to the results list
                    self.results.append(record)
    
    # Write the content of the previously populated results-list to a text file so that it can later be used to build a KnowledgeBase object
    def results_writeFile(self):
        with open('ConceptNet_Output.txt', 'a+') as cn_output:
            for record in self.results:
                cn_output.write(f"{record['start']} [{record['relation']}] {record['end']} :: {record['weight']}\n")



# TEST CODE
"""
crawler = ConceptNet_Crawler()
crawler.set_uri('start')
crawler.run_query()
crawler.json_buildrelations()

crawler.results_writeFile()
"""