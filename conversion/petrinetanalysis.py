import signal
import pm4py.simulation.playout.simulator as simulator
from pm4py.objects.log.log import EventLog, Trace


# Define alarm handler (to limit the trace computation to a certain amount of time)
def alarm_handler(signum, frame):
    raise Exception("timeout")


def get_traces(net, initial_marking, final_marking, timeout, remove_loops=True, extensive=True, no_traces=100):
    log = []

    # Signal makes sure the trace computation ends after provided timeout (default = 10 seconds)
    try:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout)
        if extensive:
            log = simulator.apply(net, initial_marking, final_marking, variant=simulator.Variants.EXTENSIVE)
        else:
            parameters = {simulator.Variants.BASIC_PLAYOUT.value.Parameters.NO_TRACES: no_traces}
            log = simulator.apply(net, initial_marking, final_marking, variant=simulator.Variants.BASIC_PLAYOUT,
                                  parameters=parameters)
    except Exception:
        print("WARNING: Time out or error during trace computation.")
        signal.alarm(0)
        return log, log

    signal.alarm(0)
    print(f"\tTraces computed: {len(log)}")

    log = filter_irrelevant_labels(log)

    # Filter traces with loops
    if remove_loops:
        log_no_loops = EventLog()
        for trace in log:
            trace_labels = [x["concept:name"] for x in trace]
            if len(trace_labels) == len(set(trace_labels)):
                log_no_loops.append(trace)
        if len(log) > len(log_no_loops):
            print("{0} traces with loops removed (out of {1})".format(str(len(log) - len(log_no_loops)), str(len(log))))
        return log, log_no_loops
    return log


def filter_irrelevant_labels(log):
    cleaned_log = EventLog()
    for trace in log:
        new_trace = Trace([event for event in trace if _is_relevant_label(event["concept:name"])])
        if len(new_trace) > 0:
            cleaned_log.append(new_trace)
    return cleaned_log


def _is_relevant_label(task_name):
    terms = {"Message"}
    if task_name == None:
        return False
    if task_name == "":
        return False
    if task_name.isnumeric():
        return False
    if task_name in terms:
        return False
    if "Gateway" in task_name:
        return False
    # if task_name.startswith("Exclusive_Databased_Gateway") \
    #         or task_name.startswith("EventbasedGateway") \
    #         or task_name.startswith("ParallelGateway") \
    #         or task_name.startswith("InclusiveGateway"):
    #     return False
    if task_name.startswith("EventSubprocess") or task_name.startswith("Subprocess"):
        return False
    return True
