from knowledgebase.knowledgerecord import Observation
import conversion.petrinetanalysis as pna
import pickle

class XESPopulator:

    def __init__(self, parser, print_records = False):
        self.parser = parser
        self.print_records = print_records

    def extract_records_from_log(self, log):
        relevant_tasks = set([x["concept:name"] for trace in log for x in trace if pna._is_relevant_label(x["concept:name"])])
        extracted_observations = []
        filtered_traces = [trace for trace in log if not has_loop(trace)]
        if len(filtered_traces) > 0:
            for t1 in relevant_tasks:
                for t2 in relevant_tasks:
                    extracted_observations.extend(self.observations_for_pair(t1, t2, filtered_traces))
        return extracted_observations

    def observations_for_pair(self, t1, t2, traces):
        observations = []
        t1_parse = self.parser.parse_label(str(t1))
        t2_parse = self.parser.parse_label(str(t2))
        # Check if tasks relates to same BO
        if t1_parse.bos == t2_parse.bos:
            # If t1 and t2 co-occur in ALL finite paths, we consider them as co-occurring
            cooccurrence = True
            # If t1 and t2 do NOT co-occur in ANY finite path, we consider them exclusive
            exclusive = True
            # If t1 is always followed by t2
            order = True

            # Check all traces (BEWARE: The checks are based on the labels only)
            for trace in traces:
                trace_labels = [x["concept:name"] for x in trace]
                if not (t1 in trace_labels) or not (t2 in trace_labels):
                    cooccurrence = False
                if t1 in trace_labels and t2 in trace_labels:
                    exclusive = False
                if t1 in trace_labels and t2 in trace_labels:
                    if trace_labels.index(t1) > trace_labels.index(t2):
                        order = False
                if exclusive:
                    order = False

            if (cooccurrence or exclusive or order):
                if len(t1_parse.actions) > 0 and len(t2_parse.actions) > 0:
                    if t1_parse.actions[0] != t2_parse.actions[0]:
                        if cooccurrence:
                            observation = (t1_parse.actions[0], t2_parse.actions[0], Observation.CO_OCC)
                            observations.append(observation)
                        if exclusive:
                            observation = (t1_parse.actions[0], t2_parse.actions[0], Observation.XOR)
                            observations.append(observation)
                        if order:
                            observation = (t1_parse.actions[0], t2_parse.actions[0], Observation.ORDER)
                            observations.append(observation)
        return observations


    # def populate(self, knowledge_base: KnowledgeBase, log, path_to_ser_kr):
    #                 for observation in extracted_observations:
    #                     knowledge_base.add_observation(observation[0], observation[1], observation[2])
    #                     # store observations for faster loading in cross-validation
    #                     write_observations_to_file(path_to_ser_kr, extracted_observations)
    #
    #                 if extracted_observations:
    #                     self.extracted = True
    #
    # def has_extracted_records(self):
    #     return self.extracted

def has_loop(trace):
    trace_labels = [x["concept:name"] for x in trace]
    return len(trace_labels) > len(set(trace_labels))


def write_observations_to_file(ser_file, observations):
    pickle.dump(observations, open(ser_file, "wb"))

