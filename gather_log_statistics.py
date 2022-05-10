import synthetic_evaluation
import pickle

from evaluation.simple_log_collection import SimpleLog


def analyze_log_collection(log_collection, parser):
    classes = []
    variants = []
    avg_lengths = []
    max_lengths = []
    bos = []
    with_loops = 0
    for log in list(log_collection.get_logs()):
        n_classes, n_variants, avg_length, max_length, n_bos, has_loop = analyze_log(log, parser)
        classes.append(n_classes)
        variants.append(n_variants)
        avg_lengths.append(avg_length)
        max_lengths.append(max_length)
        bos.append(n_bos)
        with_loops += has_loop
    print("Event classes : {0} (avg.) {1} (max)".format( str(sum(classes) / len(classes)), max(classes)))
    print("Variants : {0} (avg.) {1} (max)".format(str(sum(variants) / len(variants)), max(variants)))
    print("lenghts : {0} (avg.) {1} (max)".format(str(sum(avg_lengths) / len(avg_lengths)), max(max_lengths)))
    print("BOs : {0} (avg.) {1} (max)".format(str(sum(bos) / len(bos)), max(bos)))
    print("with loops : {0}".format(str(with_loops)))

def analyze_log(simple_log: SimpleLog, parser):
    variants = simple_log.get_variants()
    event_classes = set()
    for variant in variants:
        event_classes.update(variant)
    variant_lengths = [len(variant) for variant in variants]
    avg_length = sum(variant_lengths) / len(variants)
    max_length = max(variant_lengths)
    unique_bos = {str(parser.parse_label(event_class).bos) for event_class in event_classes}

    return len(event_classes), len(variants), avg_length, max_length, len(unique_bos), has_loop(simple_log)

def has_loop(simple_log: SimpleLog):
    for variant in simple_log.get_variants():
        for i in range(len(variant) - 1):
            for j in range(i + 1, len(variant)):
                if variant[i] == variant[j]:
                    return 1
    return 0


parser = synthetic_evaluation.load_parser()

orig_log_collection = pickle.load(open(synthetic_evaluation.orig_log_collection_file, "rb"))
print('statistics original collection')
# analyze_log_collection(orig_log_collection, parser)
print(len(orig_log_collection.get_logs()))

# noisy_log_collection = pickle.load(open(run_evaluation.noisy_log_collection_file, "rb"))
# print('\nstatistics noisy collection')
# analyze_log_collection(noisy_log_collection, parser)
