"""
@author: Gusztáv Megyesi
"""

import pickle

# Load xes records
with open('xes_serialized.ser','rb') as pickle_loader:
    xes_serialized = pickle.load(pickle_loader)

# Load Atomic records
with open('kb_atomic.ser','rb') as pickle_loader:
    kb_atomic = pickle.load(pickle_loader)

# Load ConceptNet records
with open('kb_conceptnet.ser','rb') as pickle_loader:
    kb_conceptnet = pickle.load(pickle_loader)

atomic_verbs_all = set()
atomic_objects_all = set()

conceptnet_verbs_all = set()
conceptnet_objects_all = set()

xes_verbs_all = set()
xes_objects_all = set()


# Extract distinct verb list to xes_verbs
for record in xes_serialized:
    for action in record['xes_actions']:
        xes_verbs_all.add(action)

    for object in record['xes_bos']:
        xes_objects_all.add(object)

# Extract distinct verb list to atomic_verbs
for record in kb_atomic:
    for verb in record['verb1']:
        atomic_verbs_all.add(verb)

    for verb in record['verb2']:
        atomic_verbs_all.add(verb)

    for obj in record['object1']:
        atomic_objects_all.add(obj)

    for obj in record['object2']:
        atomic_objects_all.add(obj)

# Extract distinct verb list to conceptnet_verbs
for record in kb_conceptnet:
    for verb in record['verb1']:
        conceptnet_verbs_all.add(verb)

    for verb in record['verb2']:
        conceptnet_verbs_all.add(verb)

    for obj in record['object1']:
        conceptnet_objects_all.add(obj)

    for obj in record['object2']:
        conceptnet_objects_all.add(obj)

# number of verbs in XES
nr_verbs_xes = len(xes_verbs_all)

# number of objects in XES
nr_objects_xes = len(xes_objects_all)

# number of verbs in KB-Atomic
nr_verbs_atomic = len(atomic_verbs_all)

# number of objects in KB-Atomic
nr_objects_atomic = len(atomic_objects_all)

# number of verbs covered in Atomic
nr_verbs_covered_atomic = len(xes_verbs_all.intersection(atomic_verbs_all))

# number of objects covered in Atomic
nr_objects_covered_atomic = len(xes_objects_all.intersection(atomic_objects_all))

"""
CN
"""

# number of verbs in KB-Conceptnet
nr_verbs_conceptnet = len(conceptnet_verbs_all)

# number of objects in KB-Conceptnet
nr_objects_conceptnet = len(conceptnet_objects_all)

# number of verbs covered in Conceptnet
nr_verbs_covered_conceptnet = len(xes_verbs_all.intersection(conceptnet_verbs_all))

# number of objects covered in Conceptnet
nr_objects_covered_conceptnet = len(xes_objects_all.intersection(conceptnet_verbs_all))


print(f'Atomic length: {len(kb_atomic)}')
print(f'Atomic verb number: {(nr_verbs_atomic)}')
print(f'Atomic object number: {(nr_objects_atomic)}')

print(f'Atomic verb coverage: {100*(nr_verbs_covered_atomic / nr_verbs_xes)}%')
print(f'Atomic object coverage: {100*(nr_objects_covered_atomic / nr_objects_xes)}%')

print(f'Atomic verb usability ratio: {100*(nr_verbs_covered_atomic / nr_verbs_atomic)}%')
print(f'Atomic object usability ratio: {100*(nr_objects_covered_atomic / nr_objects_atomic)}%')


print(f'ConceptNet length: {len(kb_conceptnet)}')
print(f'ConceptNet verb number: {(nr_verbs_conceptnet)}')
print(f'ConceptNet object number: {(nr_objects_conceptnet)}')

print(f'ConceptNet verb coverage: {100*(nr_verbs_covered_conceptnet / nr_verbs_xes)}%')
print(f'ConceptNet object coverage: {100*(nr_objects_covered_conceptnet / nr_objects_xes)}%')

print(f'ConceptNet verb usability ratio: {100*(nr_verbs_covered_conceptnet / nr_verbs_conceptnet)}%')
print(f'ConceptNet object usability ratio: {100*(nr_objects_covered_conceptnet / nr_objects_conceptnet)}%')






