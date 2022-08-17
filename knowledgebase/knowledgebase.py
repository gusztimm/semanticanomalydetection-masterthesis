"""
This file is part of the repository belonging to the Master Thesis of Gusztáv Megyesi - MN 1526252
Title: Incorporation of Commonsense Knowledge Resources for Semantic Anomaly Detection in Process Mining
Submitted to the Data and Web Science Group - Prof. Dr. Han van der Aa - University of Mannheim in August 2022

The original version of this file has been downloaded from the repository belonging to the following paper:
H. van der Aa, A. Rebmann, and H. Leopold, “Natural language-based detection of semantic execution anomalies in event logs,” Information Systems, vol. 102, p. 101824, Dec. 2021.
The original repository is available at https://gitlab.uni-mannheim.de/processanalytics/semanticanomalydetection
"""

from knowledgebase.knowledgerecord import KnowledgeRecord, Observation, Dataset
import labelparser.label_utils as label_utils
from gensim.utils import simple_preprocess

from knowledgebase.similaritycomputer import SimMode

class KnowledgeBase:

    dataset_ranking = {
                Dataset.VERBOCEAN : 3,
                Dataset.CONCEPTNET : 2,
                Dataset.ATOMIC : 1,
                Dataset.BPMAI : 4
    }

    def __init__(self):
        self.record_map = {}
        self.verbs = None
        self.min_support = 1
        self.apply_filter_heuristics = False
        self.filter_heuristics_rank = False
        self.filter_heuristics_cscore = False
        self.anomaly_classification = True

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

    # Limit-BO: this function treats all objects as equal (attend school vs. go to school results in attend->go to)
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

    def get_record_confidence(self, verb1, verb2, record_type, obj='', ):
        # retrieve list of record, regardless of object
        record_list = self.get_record(verb1, verb2, record_type)
        record_confidence = -1

        if record_list:
            record_confidence=0
            for record in record_list:

                # Returns count of records for ALL records with verb-pair, regardless of object
                if obj=='':
                    if record.normconf>record_confidence:
                        record_confidence=record.normconf

                # Returns count of records with NO OBJECT/OBJECT-INDEPENDENT or with SPECIFIC OBJECT
                else:
                    if record.obj in ['', obj]:
                        if record.normconf>record_confidence:
                            record_confidence=record.normconf

        return record_confidence

    # Get rank based on verb pair/object
    def get_record_rank(self, verb1, verb2, record_type, obj=''):
        # retrieve list of record, regardless of object
        record_list = self.get_record(verb1, verb2, record_type)
        record_rank = {99}

        if record_list:
            for record in record_list:

                # Returns rank of records for ALL records with verb-pair, regardless of object
                if obj=='':
                    for src in record.source:
                        record_rank.add(self.dataset_ranking[src[0]])

                # Returns rank of records with NO OBJECT/OBJECT-INDEPENDENT or with SPECIFIC OBJECT
                else:
                    if record.obj in ['', obj]:
                        for src in record.source:
                            record_rank.add(self.dataset_ranking[src[0]])

        # Return lowest rank (highest priority)
        return min(record_rank)


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

        if self.anomaly_classification==True:
            pro_cscore=-1
            cscore_order_exact_match=-1
            cscore_order_similar_records=-1

            # 0. If kb_heur is true and contradicting record, then not a violation
            if self.apply_filter_heuristics and self.get_record_count(verb1, verb2,
                                                                Observation.ORDER, obj) >= self.min_support:
                return False, -1

            # 1. Get score of exact match
            cscore_order_exact_match = self.get_record_confidence(verb2, verb1, Observation.ORDER, obj)
            pro_cscore = cscore_order_exact_match

            # 2. If no EXACT match, and EQ matching only allowed, then cannot be a violation
            if (sim_computer.sim_mode == SimMode.EQUAL) and pro_cscore==-1:
                return False, -1

             # 3. SYN or SEM config, thus need to get similar records
            if (sim_computer.sim_mode != SimMode.EQUAL):
                #GET similar records
                similar_records = self.get_similar_records_with_sim_value(verb2, verb1, Observation.ORDER, sim_computer, obj)

                if not similar_records:
                    # No similar record
                    cscore_order_similar_records = -1
                else:
                    #Get max (score*similarity) in similar records array
                    cscore_order_similar_records= max([record[0].normconf*(record[1]+record[2])/2 for record in similar_records])

            # 4. Aggregate values

            # Neither EQ nor similarity match found supporting evidence, then not a violation
            if cscore_order_exact_match==-1 and cscore_order_similar_records==-1:
                return False, -1

            #Only exact match
            if cscore_order_exact_match!=-1 and cscore_order_similar_records==-1:
                pro_cscore = cscore_order_exact_match
                return True, pro_cscore

            # Both exact and similar records TODO: Also try other configs!
            if cscore_order_exact_match!=-1 and cscore_order_similar_records!=-1:
                pro_cscore = cscore_order_exact_match+cscore_order_similar_records
                return True, pro_cscore

            #Only similar records
            if cscore_order_exact_match==-1 and cscore_order_similar_records!=-1:
                pro_cscore = cscore_order_similar_records
                return True, pro_cscore

        if self.filter_heuristics_cscore==True:
            pro_cscore=-1
            contra_cscore=-1

            # 1. check confidence of EXACT MATCH record specifying XOR relation
            cscore_order_exact_match = self.get_record_confidence(verb2, verb1, Observation.ORDER, obj)
            pro_cscore = cscore_order_exact_match

            # 2. If no EXACT match, and EQ matching only allowed, then cannot be a violation
            if (sim_computer.sim_mode == SimMode.EQUAL) and pro_cscore==-1:
                return False

            # 3. SYN or SEM config, thus need to get similar records
            if (sim_computer.sim_mode != SimMode.EQUAL):
                #GET similar records
                similar_records = self.get_similar_records_with_sim_value(verb2, verb1, Observation.ORDER, sim_computer, obj)

                if not similar_records:
                    # No similar record, rank 99
                    cscore_order_similar_records = -1
                else:
                    #Get max (score*similarity) in similar records array
                    cscore_order_similar_records= max([record[0].normconf*(record[1]+record[2])/2 for record in similar_records])

                #Neither EQ nor similarity match found supporting evidence, then not a violation
                if cscore_order_exact_match==-1 and cscore_order_similar_records==-1:
                    return False

                #Only exact match
                if cscore_order_exact_match!=-1 and cscore_order_similar_records==-1:
                    pro_cscore = cscore_order_exact_match

                #Both exact and similar records
                if cscore_order_exact_match!=-1 and cscore_order_similar_records!=-1:
                    pro_cscore = cscore_order_exact_match

                #Only similar records
                if cscore_order_exact_match==-1 and cscore_order_similar_records!=-1:
                    pro_cscore = cscore_order_similar_records

            # 4. Filtering exclusion relations: are there ORDER/CO_OCC records contradicting with BETTER or same rank?
            contra_cscore =  self.get_record_confidence(verb1, verb2, Observation.ORDER, obj)

            # 5. Compare ranks
            if contra_cscore < pro_cscore:
                return True
            else:
                return False

        if self.filter_heuristics_rank==True:
            pro_rank=99
            contra_rank=99

            # 1. check rank of EXACT MATCH record specifying XOR relation
            rank_order_exact_match = self.get_record_rank(verb2, verb1, Observation.ORDER, obj)
            pro_rank = rank_order_exact_match

            # 2. If no EXACT match, and EQ matching only allowed, then cannot be a violation
            if (sim_computer.sim_mode == SimMode.EQUAL) and pro_rank==99:
                return False

            # 3. SYN or SEM config, thus need to get similar records
            if (sim_computer.sim_mode != SimMode.EQUAL):
                #GET similar records
                similar_records = self.get_similar_records(verb2, verb1, Observation.ORDER, sim_computer, obj)

                if not similar_records:
                    # No similar record, rank 99
                    rank_order_similar_records = 99
                else:
                    #Get the rank of the most prestigious similar record
                    rank_order_similar_records= min([record.get_knowledge_record_object_rank(self.dataset_ranking) for record in similar_records])

                # Get the best-ranked record
                pro_rank = min(rank_order_exact_match, rank_order_similar_records)

                # If neither EQ nor similarity match found supporting evidence, then not a violation
                if pro_rank==99:
                    return False

            # 4. Filtering exclusion relations: are there ORDER/CO_OCC records contradicting with BETTER or same rank?
            contra_rank = self.get_record_rank(verb1, verb2, Observation.ORDER, obj)

            # 5. Compare ranks
            if pro_rank<contra_rank:
                return True
            else:
                return False
        else:
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

    def has_xor_violation(self, verb1, verb2, sim_computer, obj=''):
        # CASE 1+2.
        # if obj=='' object does NOT matter
        # if obj!='' object is differentiated, limit count to object-independent KR and object-specific KR (no unrelated objects)

        # heuristic: check if there is explicit evidence that the verbs should occur in a particular order or
        # if they are in co-occurrence relation. In either case, they should thus not be exclusive

        # Filter heuristics based on confidence score

        if self.anomaly_classification==True:
            pro_cscore=-1
            cscore_xor_exact_match = -1
            cscore_xor_similar_records = -1

            # 0. If kb_heur is true and contradicting record, then not a violation
            if self.apply_filter_heuristics and \
                    (self.get_record_count(verb1, verb2, Observation.ORDER, obj) >= self.min_support or
                    self.get_record_count(verb2, verb1, Observation.ORDER, obj) >= self.min_support or
                    self.get_record_count(verb1, verb2, Observation.CO_OCC, obj) >= self.min_support or
                    self.get_record_count(verb2, verb1, Observation.CO_OCC, obj) >= self.min_support):
                return False, -1

            # 1. Get score of exact match
            cscore_xor_exact_match = self.get_record_confidence(verb1, verb2, Observation.XOR, obj)
            pro_cscore = cscore_xor_exact_match

            # 2. If no EXACT match, and EQ matching only allowed, then cannot be a violation
            if (sim_computer.sim_mode == SimMode.EQUAL) and pro_cscore==-1:
                return False, -1

             # 3. SYN or SEM config, thus need to get similar records
            if (sim_computer.sim_mode != SimMode.EQUAL):
                #GET similar records
                similar_records = self.get_similar_records_with_sim_value(verb1, verb2, Observation.XOR, sim_computer, obj)

                if not similar_records:
                    # No similar record
                    cscore_xor_similar_records = -1
                else:
                    #Get max (score*similarity) in similar records array
                    cscore_xor_similar_records= max([record[0].normconf*(record[1]+record[2])/2 for record in similar_records])


            # 4. Aggregate values

            # Neither EQ nor similarity match found supporting evidence, then not a violation
            if cscore_xor_exact_match==-1 and cscore_xor_similar_records==-1:
                return False, -1

            #Only exact match
            if cscore_xor_exact_match!=-1 and cscore_xor_similar_records==-1:
                pro_cscore = cscore_xor_exact_match
                return True, pro_cscore

            # Both exact and similar records TODO: Also try other configs!
            if cscore_xor_exact_match!=-1 and cscore_xor_similar_records!=-1:
                pro_cscore = cscore_xor_exact_match+cscore_xor_similar_records
                return True, pro_cscore

            #Only similar records
            if cscore_xor_exact_match==-1 and cscore_xor_similar_records!=-1:
                pro_cscore = cscore_xor_similar_records
                return True, pro_cscore

        if self.filter_heuristics_cscore==True:
            pro_cscore=-1
            contra_cscore=-1

            # 1. check confidence of EXACT MATCH record specifying XOR relation
            cscore_xor_exact_match = self.get_record_confidence(verb1, verb2, Observation.XOR, obj)
            pro_cscore = cscore_xor_exact_match

            # 2. If no EXACT match, and EQ matching only allowed, then cannot be a violation
            if (sim_computer.sim_mode == SimMode.EQUAL) and pro_cscore==-1:
                return False

            # 3. SYN or SEM config, thus need to get similar records
            if (sim_computer.sim_mode != SimMode.EQUAL):
                #GET similar records
                similar_records = self.get_similar_records_with_sim_value(verb1, verb2, Observation.XOR, sim_computer, obj)

                if not similar_records:
                    # No similar record, rank 99
                    cscore_xor_similar_records = -1
                else:
                    #Get max (score*similarity) in similar records array
                    cscore_xor_similar_records= max([record[0].normconf*(record[1]+record[2])/2 for record in similar_records])

                #Neither EQ nor similarity match found supporting evidence, then not a violation
                if cscore_xor_exact_match==-1 and cscore_xor_similar_records==-1:
                    return False

                #Only exact match
                if cscore_xor_exact_match!=-1 and cscore_xor_similar_records==-1:
                    pro_cscore = cscore_xor_exact_match

                #Both exact and similar records
                if cscore_xor_exact_match!=-1 and cscore_xor_similar_records!=-1:
                    pro_cscore = cscore_xor_exact_match

                #Only similar records
                if cscore_xor_exact_match==-1 and cscore_xor_similar_records!=-1:
                    pro_cscore = cscore_xor_similar_records

            # 4. Filtering exclusion relations: are there ORDER/CO_OCC records contradicting with BETTER or same rank?
            contra_cscore =  max(self.get_record_confidence(verb1, verb2, Observation.ORDER, obj),
                                self.get_record_confidence(verb2, verb1, Observation.ORDER, obj),
                                self.get_record_confidence(verb1, verb2, Observation.CO_OCC, obj),
                                self.get_record_confidence(verb2, verb1, Observation.CO_OCC, obj))

            # 5. Compare ranks
            if contra_cscore < pro_cscore:
                return True
            else:
                return False


        # Filter heuristics based on provenance
        if self.filter_heuristics_rank==True:
            pro_rank=99
            contra_rank=99

            # 1. check rank of EXACT MATCH record specifying XOR relation
            rank_xor_exact_match = self.get_record_rank(verb1, verb2, Observation.XOR, obj)
            pro_rank = rank_xor_exact_match

            # 2. If no EXACT match, and EQ matching only allowed, then cannot be a violation
            if (sim_computer.sim_mode == SimMode.EQUAL) and pro_rank==99:
                return False

            # 3. SYN or SEM config, thus need to get similar records
            if (sim_computer.sim_mode != SimMode.EQUAL):
                #GET similar records
                similar_records = self.get_similar_records(verb1, verb2, Observation.XOR, sim_computer, obj)

                if not similar_records:
                    # No similar record, rank 99
                    rank_xor_similar_records = 99
                else:
                    #Get the rank of the most prestigious similar record
                    rank_xor_similar_records= min([record.get_knowledge_record_object_rank(self.dataset_ranking) for record in similar_records])

                # Get the best-ranked record
                pro_rank = min(rank_xor_exact_match, rank_xor_similar_records)

                # If neither EQ nor similarity match found supporting evidence, then not a violation
                if pro_rank==99:
                    return False

            # 4. Filtering exclusion relations: are there ORDER/CO_OCC records contradicting with BETTER or same rank?
            contra_rank =  min(self.get_record_rank(verb1, verb2, Observation.ORDER, obj),
                                self.get_record_rank(verb2, verb1, Observation.ORDER, obj),
                                self.get_record_rank(verb1, verb2, Observation.CO_OCC, obj),
                                self.get_record_rank(verb2, verb1, Observation.CO_OCC, obj))

            # 5. Compare ranks
            if pro_rank<contra_rank:
                return True
            else:
                return False

        # Default case: all records are equally important
        else:
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

        if self.anomaly_classification==True:
            pro_cscore=-1
            cscore_cooc_exact_match = -1
            cscore_cooc_similar_records = -1

            # 0. If kb_heur is true and contradicting record, then not a violation
            if self.apply_filter_heuristics and self.get_record_count(verb1, verb2, Observation.XOR, obj) >= self.min_support:
                return False, -1

            # 1. Get score of exact match
            cscore_cooc_exact_match = self.get_record_confidence(verb1, verb2, Observation.CO_OCC, obj)
            pro_cscore = cscore_cooc_exact_match

            # 2. If no EXACT match, and EQ matching only allowed, then cannot be a violation
            if (sim_computer.sim_mode == SimMode.EQUAL) and pro_cscore==-1:
                return False, -1

                # 3. SYN or SEM config, thus need to get similar records
            if (sim_computer.sim_mode != SimMode.EQUAL):
                #GET similar records
                similar_records = self.get_similar_records_with_sim_value(verb1, verb2, Observation.CO_OCC, sim_computer, obj)

                if not similar_records:
                    # No similar record
                    cscore_cooc_similar_records = -1
                else:
                    #Get max (score*similarity) in similar records array
                    cscore_cooc_similar_records= max([record[0].normconf*(record[1]+record[2])/2 for record in similar_records])

            # 4. Aggregate values

            # Neither EQ nor similarity match found supporting evidence, then not a violation
            if cscore_cooc_exact_match==-1 and cscore_cooc_similar_records==-1:
                return False, -1

            #Only exact match
            if cscore_cooc_exact_match!=-1 and cscore_cooc_similar_records==-1:
                pro_cscore = cscore_cooc_exact_match
                return True, pro_cscore

            # Both exact and similar records TODO: Also try other configs!
            if cscore_cooc_exact_match!=-1 and cscore_cooc_similar_records!=-1:
                pro_cscore = cscore_cooc_exact_match+cscore_cooc_similar_records
                return True, pro_cscore

            #Only similar records
            if cscore_cooc_exact_match==-1 and cscore_cooc_similar_records!=-1:
                pro_cscore = cscore_cooc_similar_records
                return True, pro_cscore

        if self.filter_heuristics_cscore==True:
            pro_cscore=-1
            contra_cscore=-1

            # 1. check confidence of EXACT MATCH record specifying XOR relation
            cscore_cooc_exact_match = self.get_record_confidence(verb1, verb2, Observation.CO_OCC, obj)
            pro_cscore = cscore_cooc_exact_match

            # 2. If no EXACT match, and EQ matching only allowed, then cannot be a violation
            if (sim_computer.sim_mode == SimMode.EQUAL) and pro_cscore==-1:
                return False

            # 3. SYN or SEM config, thus need to get similar records
            if (sim_computer.sim_mode != SimMode.EQUAL):
                #GET similar records
                similar_records = self.get_similar_records_with_sim_value(verb1, verb2, Observation.CO_OCC, sim_computer, obj)

                if not similar_records:
                    # No similar record, rank 99
                    cscore_cooc_similar_records = -1
                else:
                    #Get max (score*similarity) in similar records array
                    cscore_cooc_similar_records= max([record[0].normconf*(record[1]+record[2])/2 for record in similar_records])

                #Neither EQ nor similarity match found supporting evidence, then not a violation
                if cscore_cooc_exact_match==-1 and cscore_cooc_similar_records==-1:
                    return False

                #Only exact match
                if cscore_cooc_exact_match!=-1 and cscore_cooc_similar_records==-1:
                    pro_cscore = cscore_cooc_exact_match

                #Both exact and similar records
                if cscore_cooc_exact_match!=-1 and cscore_cooc_similar_records!=-1:
                    pro_cscore = cscore_cooc_exact_match

                #Only similar records
                if cscore_cooc_exact_match==-1 and cscore_cooc_similar_records!=-1:
                    pro_cscore = cscore_cooc_similar_records

            # 4. Filtering exclusion relations: are there ORDER/CO_OCC records contradicting with BETTER or same rank?
            contra_cscore =  self.get_record_confidence(verb1, verb2, Observation.XOR, obj)

            # 5. Compare ranks
            if contra_cscore < pro_cscore:
                return True
            else:
                return False


        if self.filter_heuristics_rank==True:
            pro_rank=99
            contra_rank=99

            # 1. check rank of EXACT MATCH record specifying CO_OCC relation
            rank_cooc_exact_match = self.get_record_rank(verb1, verb2, Observation.CO_OCC, obj)
            pro_rank = rank_cooc_exact_match

            # 2. If no EXACT match, and EQ matching only allowed, then cannot be a violation
            if (sim_computer.sim_mode == SimMode.EQUAL) and pro_rank==99:
                return False

            # 3. SYN or SEM config, thus need to get similar records
            if (sim_computer.sim_mode != SimMode.EQUAL):
                #GET similar records
                similar_records = self.get_similar_records(verb1, verb2, Observation.CO_OCC, sim_computer, obj)

                if not similar_records:
                    # No similar record, rank 99
                    rank_cooc_similar_records = 99
                else:
                    #Get the rank of the most prestigious similar record
                    rank_cooc_similar_records= min([record.get_knowledge_record_object_rank(self.dataset_ranking) for record in similar_records])

                # Get the best-ranked record
                pro_rank = min(rank_cooc_exact_match, rank_cooc_similar_records)

                # If neither EQ nor similarity match found supporting evidence, then not a violation
                if pro_rank==99:
                    return False

            # 4. Filtering exclusion relations: are there ORDER/CO_OCC records contradicting with BETTER or same rank?
            contra_rank =  self.get_record_rank(verb1, verb2, Observation.XOR, obj)

            # 5. Compare ranks
            if pro_rank<contra_rank:
                return True
            else:
                return False

        # Default case: all records are equally important
        else:
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

    # Limit-BO: get_record returns list instead of single KR, this is now considered
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

    #GM-CR: new - WITH similarity value
    def get_similar_records_with_sim_value(self, verb1, verb2, record_type, sim_computer, obj=''):
            sim_verbs1 = self._get_sim_verbs(verb1, sim_computer, include_sim_value=True)
            sim_verbs2 = self._get_sim_verbs(verb2, sim_computer, include_sim_value=True)

            records = []

            if not sim_computer.match_one:
                # both verbs in a record may differ from original ones
                for sim_verb1 in sim_verbs1:
                    for sim_verb2 in sim_verbs2:
                        if self.get_record(sim_verb1[0], sim_verb2[0], record_type):

                            #get list of records with ggf. different objects
                            sim_value_verb1 = sim_verb1[1]
                            sim_value_verb2 = sim_verb2[1]

                            records_to_append = self.get_record(sim_verb1[0], sim_verb2[0], record_type)

                            #add each of them
                            # if obj does NOT matter, use all records
                            # if obj does MATTER, only use object-independent and object-specific records

                            for record in records_to_append:

                                if obj=='':
                                    records.append((record,sim_value_verb1,sim_value_verb2))
                                else:
                                    if obj in ['',obj]:
                                        records.append((record,sim_value_verb1,sim_value_verb2))

                            #OLD: records.append(self.get_record(sim_verb1, sim_verb2, record_type))
            else:
                #     requires that at least one verb in record corresponds to original one
                for sim_verb1 in sim_verbs1:
                    if self.get_record(sim_verb1[0], verb2, record_type):

                        #save sim value
                        sim_value = sim_verb1[1]

                        #get list of records with ggf. different objects
                        records_to_append = self.get_record(sim_verb1[0], verb2, record_type)

                        #add each of them
                        # if obj does NOT matter, use all records
                        # if obj does MATTER, only use object-independent and object-specific records
                        for record in records_to_append:

                            if obj=='':
                                records.append((record,sim_value,1))
                            else:
                                if obj in ['',obj]:
                                    records.append((record,sim_value,1))

                for sim_verb2 in sim_verbs2:
                    if self.get_record(verb1, sim_verb2[0], record_type):

                        #save sim value
                        sim_value = sim_verb2[1]

                        #get list of records with ggf. different objects
                        records_to_append = self.get_record(verb1, sim_verb2[0], record_type)

                        #add each of them
                        # if obj does NOT matter, use all records
                        # if obj does MATTER, only use object-independent and object-specific records
                        for record in records_to_append:

                            if obj=='':
                                records.append((record,1,sim_value))
                            else:
                                if obj in ['',obj]:
                                    records.append((record,1,sim_value))

            return records

    def _get_sim_verbs(self, verb, sim_computer, include_sim_value=False):
        verb = label_utils.lemmatize_word(verb)
        sim_verbs = []

        if sim_computer.sim_mode == SimMode.SYNONYM:
            sim_verbs = sim_computer.get_synonyms(verb)

        # For synonyms, get flat sim value of 0.5
        # If sim_value is required, then get list of tuples [('accept',0.5),('approve'),0.5]
        # If sim is not required, then list of verbs only ['accept','approve']
            if include_sim_value:
                sim_verbs = list(zip(sim_verbs,[0.5]*len(sim_verbs)))

        # If sim_value is required, then get list of tuples [('accept',0.95),('approve'),0.92]
        # If sim is not required, then list of verbs only ['accept','approve']
        if sim_computer.sim_mode == SimMode.SEMANTIC_SIM:
            if include_sim_value:
                sim_verbs = sim_computer.compute_semantic_sim_verbs_with_similarity_value(verb)
            else:
                sim_verbs = sim_computer.compute_semantic_sim_verbs(verb, self.get_all_verbs())

        # filter out any verb that opposeses the original verb

        if include_sim_value:
            sim_verbs = [sim_verb_tuple for sim_verb_tuple in sim_verbs if not self.get_record(verb, sim_verb_tuple[0], Observation.XOR)]
        else:
            sim_verbs = [sim_verb for sim_verb in sim_verbs if not self.get_record(verb, sim_verb, Observation.XOR)]

        return sim_verbs

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
    

    def set_norm_confidence_for_all_records(self):


        #Extract normalized confidence for single record
        #If included in several datasets, add up
        #If included several times in same dataset, get highest conf

        for key, knowledge_record in self.record_map.items():
            norm_confidence = 0
            conf_dict = {}

            # If single source, then just copy normalized conf score, and jump to next
            if len(knowledge_record.source)==1:

                for src in knowledge_record.source:
                    knowledge_record.normconf=src[1]
                continue

            else:
                # More sources: iterate over each source
                for src in knowledge_record.source:
                    # Extract values
                    dataset = src[0]
                    conf = src[1]

                    # No conf for that dataset - add it
                    if dataset not in conf_dict.keys():
                        conf_dict[dataset] = conf
                    # Duplicate in same dataset - check if new value is higher
                    else:
                        existing_conf = conf_dict[dataset]

                        # If higher, then overwrite
                        if conf>existing_conf:
                            conf_dict[dataset] = conf

                # add up conf scores
                for key, value in conf_dict.items():
                    norm_confidence+=value

            knowledge_record.normconf = norm_confidence


    def filter_out_conflicting_records(self):
        pass


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
