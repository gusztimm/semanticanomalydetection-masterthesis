from knowledgebase.knowledgerecord import KnowledgeRecord, Observation
import labelparser.label_utils as label_utils
from gensim.utils import simple_preprocess

from knowledgebase.similaritycomputer import SimMode

"""
@GM: object property extended
"""

class KnowledgeBase:

    def __init__(self):
        self.record_map = {}
        self.verbs = None
        self.min_support = 1
        self.apply_filter_heuristics = False

    def get_record_object_match(self, verb1, verb2, record_type, obj):
        verb1 = label_utils.lemmatize_word(verb1)
        verb2 = label_utils.lemmatize_word(verb2)

        # symmetric XOR records are always stored in lexical order
        if record_type == Observation.XOR and verb2 > verb1:
            verb1, verb2 = verb2, verb1

         #retrieve records    
        if (verb1, verb2, obj, record_type) in self.record_map:
            return self.record_map[(verb1, verb2, obj, record_type)]

        return None

    # GM-OBJ: obj added
    # now returns a list of matching records instead of single record
    def get_record(self, verb1, verb2, record_type):
        verb1 = label_utils.lemmatize_word(verb1)
        verb2 = label_utils.lemmatize_word(verb2)

        # symmetric XOR records are always stored in lexical order
        if record_type == Observation.XOR and verb2 > verb1:
            verb1, verb2 = verb2, verb1

        # get all keys which contain verb1, verb2 regardless of object, with correct relation!
        matched_keys = [key for key in self.record_map.keys() if key[0]==verb1 and key[1]==verb2 and key[3]==record_type]

        # get the corresponding values
        record_results = [self.record_map[key] for key in matched_keys]

        if len(record_results)>0:
            return record_results
        return None

    # GM-OBJ: obj added
    # GM-OBJ: this function treats all objects as equal (attend school vs. go to school results in attend->go to)
    def get_record_count(self, verb1, verb2, record_type, obj=''):
        # retrieve list of record, regardless of object
        record_list = self.get_record(verb1, verb2, record_type)
        record_count = 0

        if record_list:
            for record in record_list:

                # Returns count of records for ALL records with verb-pair, regardless of object
                if obj=='':
                    record_count+=record.count

                # Returns count of records with NO OBJECT/OBJECT-INDEPENDENT or with SPECIFIC OBJECT
                else:
                    if record.obj in ['', obj]:
                        record_count+=record.count
        return record_count
        
    # GM-OBJ: obj added
    def add_observation(self, verb1, verb2, obj, record_type, dataset, conf, count=1):
        # ensure consistent ordering for symmetric XOR records
        if record_type == Observation.XOR and verb2 > verb1:
            verb1, verb2 = verb2, verb1

        record = self.get_record_object_match(verb1, verb2, record_type, obj)
        if record is not None:
            record.increment_count(count)
            record.add_source(dataset, conf)
        else:
            self.add_new_record(verb1, verb2, obj, record_type, count, dataset, conf)

    # GM-OBJ: obj added
    def add_new_record(self, verb1, verb2, obj, record_type, count, dataset, conf):
        verb1 = label_utils.lemmatize_word(verb1)
        verb2 = label_utils.lemmatize_word(verb2)
        obj = obj
        source = {(dataset, conf)} #set() object with a single tuple (VERBOCEAN, 1,0)

        # ensure consistent ordering for symmetric XOR records
        if record_type == Observation.XOR and verb2 > verb1:
            verb1, verb2 = verb2, verb1
        self.record_map[(verb1, verb2, obj, record_type)] = KnowledgeRecord(verb1, verb2, record_type, obj, count, source)
            
    #Never used
    """
        def has_violation(self, violation_type, verb1, verb2, sim_computer):
            if violation_type == Observation.ORDER:
                return self.has_order_violation(verb1, verb2, sim_computer)
            if violation_type == Observation.XOR:
                return self.has_xor_violation(verb1, verb2, sim_computer)
            if violation_type == Observation.CO_OCC:
                return self.has_cooc_dependency(verb1, verb2, sim_computer)
            return False
    """
    def has_order_violation(self, verb1, verb2, sim_computer, obj=''):
        # heuristic: check if there is explicit evidence that verb1 can occur before verb2
        if self.apply_filter_heuristics and self.get_record_count(verb1, verb2,
                                                                  Observation.ORDER, obj) >= self.min_support:
            return False
        # first check if there is a record that specifies that verb2 should occur before verb1
        if self.get_record_count(verb2, verb1, Observation.ORDER, obj) >= self.min_support:
            return True
        # if only equal verb matching, cannot be a violation anymore
        if sim_computer.sim_mode == SimMode.EQUAL:
            return False
        # else, get similar records that imply violations and check if any of them have sufficient support
        similar_records = self.get_similar_records(verb2, verb1, Observation.ORDER, sim_computer, obj)
        is_violation = any([record.count >= self.min_support for record in similar_records])
        return is_violation

    """
    def has_xor_violation(self, verb1, verb2, sim_computer):
        # heuristic: check if there is explicit evidence that the verbs should occur in a particular order or
        # if they are in co-occurrence relation. In either case, they should thus not be exclusive
        if self.apply_filter_heuristics and \
                (self.get_record_count(verb1, verb2, Observation.ORDER) >= self.min_support or
                 self.get_record_count(verb2, verb1, Observation.ORDER) >= self.min_support or
                 self.get_record_count(verb1, verb2, Observation.CO_OCC) >= self.min_support or
                 self.get_record_count(verb2, verb1, Observation.CO_OCC) >= self.min_support):
            return False
        # first check if there is a record that specifies that verb1 and verb2 should be exclusive
        if self.get_record_count(verb1, verb2, Observation.XOR) >= self.min_support:
            return True
        # if only equal verb matching, cannot be a violation anymore
        if sim_computer.sim_mode == SimMode.EQUAL:
            return False
        # else, get similar records that imply violations and check if any of them have sufficient support
        similar_records = self.get_similar_records(verb1, verb2, Observation.XOR, sim_computer)
        is_violation = any([record.count >= self.min_support for record in similar_records])
        return is_violation
    """

    def has_xor_violation(self, verb1, verb2, sim_computer, obj=''):
        # CASE 1+2.
        # if obj=='' object does NOT matter
        # if obj!='' object is differentiated, limit count to object-independent KR and object-specific KR (no unrelated objects)

        # heuristic: check if there is explicit evidence that the verbs should occur in a particular order or
        # if they are in co-occurrence relation. In either case, they should thus not be exclusive

        if self.apply_filter_heuristics and \
                (self.get_record_count(verb1, verb2, Observation.ORDER, obj) >= self.min_support or
                self.get_record_count(verb2, verb1, Observation.ORDER, obj) >= self.min_support or
                self.get_record_count(verb1, verb2, Observation.CO_OCC, obj) >= self.min_support or
                self.get_record_count(verb2, verb1, Observation.CO_OCC, obj) >= self.min_support):
            return False

        # first check if there is a record that specifies that verb1 and verb2 should be exclusive
        if self.get_record_count(verb1, verb2, Observation.XOR, obj) >= self.min_support:
            return True
        # if only equal verb matching, cannot be a violation anymore
        if sim_computer.sim_mode == SimMode.EQUAL:
            return False
        # else, get similar records that imply violations and check if any of them have sufficient support
        similar_records = self.get_similar_records(verb1, verb2, Observation.XOR, sim_computer, obj)
        is_violation = any([record.count >= self.min_support for record in similar_records])
        return is_violation

    def has_cooc_dependency(self, verb1, verb2, sim_computer, obj=''):
        # heuristic: there cannot be a co-occurence dependency if these records are supposed to be exclusive
        if self.apply_filter_heuristics and self.get_record_count(verb1, verb2,
                                                                  Observation.XOR, obj) >= self.min_support:
            return False
        # first check if there is a record that specifies that verb1 and verb2 should co-occur
        if self.get_record_count(verb1, verb2, Observation.CO_OCC, obj) >= self.min_support:
            return True
        # if only equal verb matching, cannot be a dependency
        if sim_computer.sim_mode == SimMode.EQUAL:
            return False
        # else, get similar records that imply co-occurrence dependencies
        similar_records = self.get_similar_records(verb1, verb2, Observation.CO_OCC, sim_computer, obj)
        has_dependency = any([record.count >= self.min_support for record in similar_records])
        return has_dependency

    # GM-OBJ: get_record returns list instead of single KR, this is now considered
    def get_similar_records(self, verb1, verb2, record_type, sim_computer, obj=''):
        sim_verbs1 = self._get_sim_verbs(verb1, sim_computer)
        sim_verbs2 = self._get_sim_verbs(verb2, sim_computer)
        records = []
        if not sim_computer.match_one:
            # both verbs in a record may differ from original ones
            for sim_verb1 in sim_verbs1:
                for sim_verb2 in sim_verbs2:
                    if self.get_record(sim_verb1, sim_verb2, record_type):

                        #get list of records with ggf. different objects
                        records_to_append = self.get_record(sim_verb1, sim_verb2, record_type)

                        #add each of them
                        # if obj does NOT matter, use all records
                        # if obj does MATTER, only use object-independent and object-specific records
                        for record in records_to_append:

                            if obj=='':                            
                                records.append(record)
                            else:
                                if obj in ['',obj]:
                                    records.append(record)

                        #OLD: records.append(self.get_record(sim_verb1, sim_verb2, record_type))
        else:
            #     requires that at least one verb in record corresponds to original one
            for sim_verb1 in sim_verbs1:
                if self.get_record(sim_verb1, verb2, record_type):

                    #get list of records with ggf. different objects
                    records_to_append = self.get_record(sim_verb1, verb2, record_type)

                    #add each of them
                    # if obj does NOT matter, use all records
                    # if obj does MATTER, only use object-independent and object-specific records
                    for record in records_to_append:

                        if obj=='':                            
                            records.append(record)
                        else:
                            if obj in ['',obj]:
                                records.append(record)

                    # OLD: records.append(self.get_record(sim_verb1, verb2, record_type))

            for sim_verb2 in sim_verbs2:
                if self.get_record(verb1, sim_verb2, record_type):

                    #get list of records with ggf. different objects
                    records_to_append = self.get_record(verb1, sim_verb2, record_type)

                    #add each of them
                    # if obj does NOT matter, use all records
                    # if obj does MATTER, only use object-independent and object-specific records
                    for record in records_to_append:

                        if obj=='':                            
                            records.append(record)
                        else:
                            if obj in ['',obj]:
                                records.append(record)
                    # OLD: records.append(self.get_record(verb1, sim_verb2, record_type))
        return records

    def _get_sim_verbs(self, verb, sim_computer):
        verb = label_utils.lemmatize_word(verb)
        sim_verbs = []
        if sim_computer.sim_mode == SimMode.SYNONYM:
            sim_verbs = sim_computer.get_synonyms(verb)
        if sim_computer.sim_mode == SimMode.SEMANTIC_SIM:
            sim_verbs = sim_computer.compute_semantic_sim_verbs(verb, self.get_all_verbs())
        # filter out any verb that opposeses the original verb
        sim_verbs = [sim_verb for sim_verb in sim_verbs if not self.get_record(verb, sim_verb, Observation.XOR)]
        return sim_verbs

    # TODO clarify what this is doing, never used
    def filter_out_conflicting_records(self):
        new_map = {}
        for (verb1, verb2, record_type) in self.record_map:
            # filter out conflicting exclusion constraints
            # logic: if there is a cooccurrence or order constraint involving two verbs, then they cannot be exclusive
            if record_type == Observation.XOR:
                record_count = self.get_record_count(verb1, verb2, record_type)
                other_counts = self.get_record_count(verb1, verb2, Observation.CO_OCC) + \
                               self.get_record_count(verb1, verb2, Observation.ORDER) + \
                               self.get_record_count(verb2, verb1, Observation.ORDER)
                if record_count > other_counts:
                    new_map[(verb1, verb2, record_type)] = self.record_map[(verb1, verb2, record_type)]
                else:
                    print('removing', (verb1, verb2, record_type, record_count), "from kb. Other count:", other_counts)
            # filter out conflicting ordering constraints
            # logic: only keep this order constraint if the reverse is less common
            if record_type == Observation.ORDER:
                order_count = self.get_record_count(verb1, verb2, record_type)
                reverse_count = self.get_record_count(verb2, verb1, record_type)
                if order_count > reverse_count:
                    new_map[(verb1, verb2, record_type)] = self.record_map[(verb1, verb2, record_type)]
                else:
                    print('removing', (verb1, verb2, record_type, order_count), "from kb. Reverse count:",
                          reverse_count)
            # filter out conflicting co-occurrence constraints
            if record_type == Observation.CO_OCC:
                new_map[(verb1, verb2, record_type)] = self.record_map[(verb1, verb2, record_type)]
                # co_occ_count = self.get_record_count(verb1, verb2, record_type)
                # xor_count = self.get_record_count(verb1, verb2, Observation.XOR)
                # if co_occ_count > xor_count:
                #     new_map[(verb1, verb2, record_type)] = self.record_map[(verb1, verb2, record_type)]
                # else:
                #     print('removing', (verb1, verb2, record_type, co_occ_count), "from kb. XOR count:",
                #           xor_count)
        self.record_map = new_map

    def get_all_verbs(self):
        if not self.verbs:
            res = set()
            for record in self.record_map.values():
                res.add(record.verb1)
                res.add(record.verb2)
            self.verbs = list(res)
        return self.verbs

    def get_record_numbers(self):
        count_order = len([record for record in self.record_map.values() if record.record_type == Observation.ORDER])
        count_xor = len([record for record in self.record_map.values() if record.record_type == Observation.XOR])
        count_coocc = len([record for record in self.record_map.values() if record.record_type == Observation.CO_OCC])
        return (count_xor, count_order, count_coocc, len(self.record_map))

    def print_most_common_records(self):
        newlist = sorted(self.record_map.values(), key=lambda x: x.count, reverse=True)
        for i in range(0, 20):
            print(newlist[i])
