import gensim.downloader as api
from enum import Enum
from gensim.corpora import Dictionary
from gensim.models import WordEmbeddingSimilarityIndex
from gensim.similarities import SparseTermSimilarityMatrix
from gensim.similarities import SoftCosineSimilarity
from gensim.utils import simple_preprocess
from nltk.corpus import wordnet
from itertools import chain
from labelparser import label_utils


class SimMode(Enum):
    EQUAL = 1,
    SYNONYM = 2,
    SEMANTIC_SIM = 3


class SimilarityComputer:

    def __init__(self, sim_mode=SimMode.EQUAL):
        self.sim_mode = sim_mode

    def __repr__(self):
        return "equal_verb_matching"

class SemanticSimilarityComputer(SimilarityComputer):

    def __init__(self, sim_threshold=1.0, compute_sim_per_log=True, match_one=False):
        self.sim_mode = SimMode.SEMANTIC_SIM
        self.sim_threshold = sim_threshold
        self.compute_sim_per_log = compute_sim_per_log
        self.match_one = match_one
        self.glove = None
        self.dictionary = None
        self.docsim_index = None
        self.verb_list = []
        self.sim_verbs_map = {}
        self.synonym_map = {}

    def __repr__(self):
        return "SEMANTIC_SIM (" + str(self.sim_threshold) + " matchone_" + str(self.match_one) + ")"

    def initialize_similarities(self, kb_verbs, log_verbs):
        print("computing semantic similarity matrix")
        # Preprocess the documents, including the query string
        kb_verbs = [simple_preprocess(verb) for verb in kb_verbs]
        log_verbs = [simple_preprocess(verb) for verb in log_verbs]

        # Load the model: this is a big file, can take a while to download and open
        if not self.glove:
            self.glove = api.load("glove-wiki-gigaword-50")
        similarity_index = WordEmbeddingSimilarityIndex(self.glove)

        # Create the term similarity matrix.
        dictionary = Dictionary(kb_verbs + log_verbs)
        similarity_matrix = SparseTermSimilarityMatrix(similarity_index, dictionary)

        bow_corpus = [dictionary.doc2bow(document) for document in kb_verbs]
        docsim_index = SoftCosineSimilarity(bow_corpus, similarity_matrix, num_best=20)
        print("semantic sims computed")
        self.verb_list = kb_verbs
        self.dictionary = dictionary
        self.docsim_index = docsim_index
        return kb_verbs, dictionary, docsim_index

    def set_loaded_similarities(self, kb_verbs, dictionary, docsim_index):
        self.verb_list = kb_verbs
        self.dictionary = dictionary
        self.docsim_index = docsim_index

    def compute_semantic_sim_verbs(self, verb, relevant_verbs):
        if verb in self.sim_verbs_map:
            return self.sim_verbs_map[verb]
        sims = self.docsim_index[self.dictionary.doc2bow(simple_preprocess(verb))]
        sim_verbs = [self.verb_list[index] for (index, sim) in sims if sim >= self.sim_threshold]
                     # and self.verb_list[index] in relevant_verbs]
        if [verb] not in sim_verbs:
            sim_verbs.append([verb])
        sim_verbs = [sim_verb[0] for sim_verb in sim_verbs]
        return sim_verbs

    def compute_semantic_sim_verbs_with_similarity_value(self, verb):
        lemmatized_verb = label_utils.lemmatize_word(verb)

        if verb in self.sim_verbs_map:
            return self.sim_verbs_map[verb]
        sims = self.docsim_index[self.dictionary.doc2bow(simple_preprocess(verb))]
        sim_verbs = [(self.verb_list[index],sim) for (index, sim) in sims if sim >= self.sim_threshold]
        
        sim_verbs_with_sim = []
        for sim_verb_tuple in sim_verbs:
        
            sim_verb = sim_verb_tuple[0]
            sim_verb_sim = sim_verb_tuple[1]

            # if similar verb's lemmatized form is verb itself, then it's rubbish - e.g. accept vs. accepted/accepting
            if verb==sim_verb[0] or (verb!=sim_verb[0] and lemmatized_verb!=label_utils.lemmatize_word(sim_verb[0])):
                sim_verbs_with_sim.append((sim_verb[0], sim_verb_sim))

        return sim_verbs_with_sim


class SynonymSimilarityComputer(SimilarityComputer):
    def __init__(self, match_one=False):
        self.sim_mode = SimMode.SYNONYM
        self.match_one = match_one
        self.synonym_map = {}

    def __repr__(self):
        return "SYNONYMOUS similarity (matchone_" + str(self.match_one) + ")"

    def get_synonyms(self, verb):
        lemma = label_utils.lemmatize_word(verb)
        if lemma in self.synonym_map:
            return self.synonym_map[lemma]
        synsets = wordnet.synsets(lemma)
        synonyms = set(chain.from_iterable([word.lemma_names() for word in synsets]))
        synonyms.add(lemma)
        self.synonym_map[lemma] = synonyms
        return synonyms
    
    def get_noun_synonyms(self, noun):
        lemma = label_utils.lemmatize_noun(noun)
        if lemma in self.synonym_map:
            return self.synonym_map[lemma]
        synsets = wordnet.synsets(lemma, pos=wordnet.NOUN)
        synonyms = set(chain.from_iterable([word.lemma_names() for word in synsets]))
        synonyms.add(lemma)
        self.synonym_map[lemma] = synonyms
        return synonyms

class ObjectSemanticSimilarityComputer(SimilarityComputer):

    def __init__(self, sim_threshold=1.0, compute_sim_per_log=True, match_one=False):
        self.sim_mode = SimMode.SEMANTIC_SIM
        self.sim_threshold = sim_threshold
        self.compute_sim_per_log = compute_sim_per_log
        self.match_one = match_one
        self.glove = None
        self.dictionary = None
        self.docsim_index = None
        self.obj_list = []
        self.sim_objects_map = {}
        self.synonym_map = {}

    def __repr__(self):
        return "SEMANTIC_SIM (" + str(self.sim_threshold) + " matchone_" + str(self.match_one) + ")"

    def initialize_similarities(self, objects):
        print("computing semantic similarity matrix")
        # Preprocess the documents, including the query string
        object_list = [simple_preprocess(obj) for obj in objects]

        # Load the model: this is a big file, can take a while to download and open
        if not self.glove:
            self.glove = api.load("glove-wiki-gigaword-50")
        similarity_index = WordEmbeddingSimilarityIndex(self.glove)

        # Create the term similarity matrix.
        dictionary = Dictionary(object_list)
        similarity_matrix = SparseTermSimilarityMatrix(similarity_index, dictionary)

        bow_corpus = [dictionary.doc2bow(document) for document in object_list]
        docsim_index = SoftCosineSimilarity(bow_corpus, similarity_matrix, num_best=20)
        print("semantic sims computed")
        self.obj_list = object_list
        self.dictionary = dictionary
        self.docsim_index = docsim_index
        return object_list, dictionary, docsim_index

    def set_loaded_similarities(self, obj_list, dictionary, docsim_index):
        self.obj_list = obj_list
        self.dictionary = dictionary
        self.docsim_index = docsim_index

    def compute_semantic_sim_objects(self, obj, relevant_verbs):
        if obj in self.sim_objects_map:
            return self.sim_objects_map[obj]
        sims = self.docsim_index[self.dictionary.doc2bow(simple_preprocess(obj))]
        sim_objects = [self.obj_list[index] for (index, sim) in sims if sim >= self.sim_threshold]
                     # and self.verb_list[index] in relevant_verbs]
        if [obj] not in sim_objects:
            sim_objects.append([obj])
        sim_objects = [sim_obj[0] for sim_obj in sim_objects]
        return sim_objects

