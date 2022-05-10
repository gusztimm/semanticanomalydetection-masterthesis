from knowledgebase.similaritycomputer import SimMode, SimilarityComputer, SemanticSimilarityComputer, \
    SynonymSimilarityComputer, ObjectSemanticSimilarityComputer
import pickle

simcomputer = ObjectSemanticSimilarityComputer(sim_threshold=0.1)

labels = ['receipt',
'repair',
'boarding pass',
'info',
'student',
'pupil',
'scholar',
'freshman',
'schoolboy',
'schoolgirl'
'money',
'order']

object_list, dictionary, docsim_index = simcomputer.initialize_similarities(labels)
pickle.dump((object_list, dictionary, docsim_index), open('test_object_similarities.ser', "wb"))

"""
#read file
object_list, dictionary, docsim_index = pickle.load(open('test_object_similarities.ser', "rb"))
"""

#load attributes
simcomputer.set_loaded_similarities(object_list, dictionary, docsim_index)

sim_objects = simcomputer.compute_semantic_sim_objects('student', [])
print(sim_objects)
