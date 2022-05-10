from copy import deepcopy
import random
import conversion.bpmnjsonanalyzer as bpmn_analyzer
from pm4py.objects.log.log import Event, Trace, EventLog


def simulate_log_from_json(file_path, log_size=0):
    # load json
    follows, labels, tasks = bpmn_analyzer.loadJSON(file_path)
    # generate initial log
    return _obtain_base_log(follows, labels, tasks, log_size)


def insert_noise(log, noisy_trace_prob, noisy_event_prob, log_size):
    if len(log) < log_size:
        # add additional traces until desired log size reached
        log_cpy = EventLog()
        for i in range(0, log_size):
            log_cpy.append(deepcopy(log[i % len(log)]))
        log = log_cpy
    classes = _get_event_classes(log)
    log_new = EventLog()
    for trace in log:
        if len(trace) > 0:
            trace_cpy = deepcopy(trace)
            # check if trace makes random selection
            if random.random() <= noisy_trace_prob:
                insert_more_noise = True
                while insert_more_noise:
                    # randomly select which kind of noise to insert
                    noise_type = random.randint(0, 2)
                    if noise_type == 0:
                        _remove_event(trace_cpy)
                    if noise_type == 1:
                        _insert_event(trace_cpy, classes)
                    if noise_type == 2:
                        _swap_events(trace_cpy)
                    # flip coin to see if more noise will be inserted
                    insert_more_noise = (random.random() <= noisy_event_prob)
            log_new.append(trace_cpy)
    return log_new


def _remove_event(trace: Trace):
    del_index = random.randint(0, len(trace) - 1)
    trace2 = Trace()
    for i in range(0, len(trace)):
        if i != del_index:
            trace2.append(trace[i])
    return trace2


def _insert_event(trace: Trace, tasks):
    ins_index = random.randint(0, len(trace))
    task = random.choice(list(tasks))
    e = Event()
    e["concept:name"] = task
    trace.insert(ins_index, e)
    return trace


def _swap_events(trace: Trace):
    if len(trace) == 1:
        return trace
    indices = list(range(len(trace)))
    index1 = random.choice(indices)
    indices.remove(index1)
    index2 = random.choice(indices)
    trace2 = Trace()
    for i in range(len(trace)):
        if i == index1:
            trace2.append(trace[index2])
        elif i == index2:
            trace2.append(trace[index1])
        else:
            trace2.append(trace[i])
    return trace2


def _obtain_base_log(follows, labels, tasks, log_size=0):
    paths = bpmn_analyzer.compute_finite_paths_of_tasks(follows, labels, tasks)

    log = EventLog()
    for path in paths:
        # print(path)
        trace = Trace()
        for task in path:
            e = Event()
            e["concept:name"] = task
            trace.append(e)
        log.append(trace)
    if len(log) >= log_size or len(log) == 0:
        return log
    # add additional traces until desired log size reached
    log_cpy = EventLog()
    for i in range(0, log_size):
        log_cpy.append(deepcopy(log[i % len(log)]))
    return log_cpy


def _get_event_classes(log):
    classes = set()
    for trace in log:
        for event in trace:
            classes.add(event["concept:name"])
    return classes
