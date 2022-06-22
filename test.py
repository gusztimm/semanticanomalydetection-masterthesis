import pickle, sys
from knowledgebase.knowledgerecord import Observation
import matplotlib.pyplot as plt

raw_equal = pickle.load(open('output/simmode_SimMode.EQUAL.ser', 'rb'))
d = raw_equal.log_result_map

tp_overall=0
fp_overall=0

tp_xor=0
fp_xor=0

tp_order=0
fp_order=0

tp_cooc=0
fp_cooc=0

true_scores = []
false_scores = []

for key, logevaluationresult in d.items():
    
    tp_overall+=len(logevaluationresult.true_anomalies)
    fp_overall+=len(logevaluationresult.false_anomalies)

    for true_anomaly_tuple in logevaluationresult.true_anomalies:
        true_anomaly = true_anomaly_tuple[0]
        true_scores.append(true_anomaly.score)

        if true_anomaly.anomaly_type == Observation.ORDER:
            tp_order+=1
        if true_anomaly.anomaly_type == Observation.XOR:
            tp_xor+=1
        if true_anomaly.anomaly_type == Observation.CO_OCC:
            tp_cooc+=1

    for false_anomaly_tuple in logevaluationresult.false_anomalies:
        false_anomaly = false_anomaly_tuple[0]   
        false_scores.append(false_anomaly.score)     

        if false_anomaly.anomaly_type == Observation.ORDER:
            fp_order+=1
        if false_anomaly.anomaly_type == Observation.XOR:
            fp_xor+=1
        if false_anomaly.anomaly_type == Observation.CO_OCC:
            fp_cooc+=1

print(f'TP overall: {tp_overall}')
print(f'FP overall: {fp_overall}')

print(f'TP XOR: {tp_xor}')
print(f'FP XOR: {fp_xor}')

print(f'TP ORDER: {tp_order}')
print(f'FP ORDER: {fp_order}')

print(f'TP CO_OCC: {tp_cooc}')
print(f'FP CO_OCC: {fp_cooc}')


plt.hist(true_scores, bins=50)
plt.gca().set(title='True Score Histogram', xlabel='Score', ylabel='Frequency')
plt.show()

plt.hist(false_scores, bins=50)
plt.gca().set(title='True Score Histogram', xlabel='Score', ylabel='Frequency')
plt.show()

