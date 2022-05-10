from collections import Counter

from pm4py.objects.log.log import Event, Trace

from labelparser import label_utils


class SimpleLog:

    def __init__(self, event_key="concept:name"):
        self.event_to_id_map = {}
        self.id_to_event_map = {}
        self.variant_counter = Counter()
        self.event_key = event_key

    def add_trace(self, trace):
        variant_tuple = tuple(
            [self._event_class_to_id(label_utils.sanitize_label(event[self.event_key])) for event in trace])
        self.variant_counter[variant_tuple] += 1

    def _event_class_to_id(self, event_class):
        if not event_class in self.event_to_id_map:
            class_id = len(self.event_to_id_map) + 1
            self.event_to_id_map[event_class] = class_id
            self.id_to_event_map[class_id] = event_class
        return self.event_to_id_map[event_class]

    def _tuple_to_variant_list(self, variant_tuple):
        return [self.id_to_event_map[class_id] for class_id in variant_tuple]

    def get_variants(self):
        return [self._tuple_to_variant_list(variant_tuple) for variant_tuple in self.variant_counter.keys()]

    def variant_count(self, variant):
        variant_tuple = tuple([self._event_class_to_id(event) for event in variant])
        return self.variant_counter.get(variant_tuple)

    def total_traces(self):
        return sum(self.variant_counter.values())


class SimpleLogCollection:

    def __init__(self):
        self.log_map = {}

    def add_log(self, log_name, log, event_key="concept:name"):
        simple_log = turn_into_simple_log(log, event_key)
        self.log_map[log_name] = simple_log

    def get_log(self, log_name):
        if log_name.endswith(".xes"):
            return self.log_map.get(log_name)
        return self.log_map.get(log_name + ".xes")

    def get_log_names(self):
        return self.log_map.keys()

    def get_logs(self):
        return self.log_map.values()

def turn_into_simple_log(log, event_key="concept:name"):
    simple_log = SimpleLog(event_key)
    for trace in log:
        simple_log.add_trace(trace)
    return simple_log


def string_sequence_to_trace(variant, event_key="concept:name"):
    return Trace([Event({event_key: event}) for event in variant])
