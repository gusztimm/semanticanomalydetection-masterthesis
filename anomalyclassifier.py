import pickle, sys
from knowledgebase.knowledgerecord import Observation
import matplotlib.pyplot as plt

class AnomalyClassifier:

    chunk_increment = 0.05
    ser_file = 'output/04_AnomalyClassification/KBExtended/raw_results/simmode_SimMode.SYNONYMkbheuristics_Trueanomalyclassification_True.ser'

    def __init__(self):
        self.log_result_map = pickle.load(open(self.ser_file, 'rb')).log_result_map
        self.anomaly_list = self.get_all_anomalies() # (Observation.TYPE, score, True/False) e.g. (Observation.ORDER, 0.255630, True)

    def get_all_anomalies(self):
        anomaly_list=[]

        for key, logevaluationresult in self.log_result_map.items():
            for true_anomaly_tuple in logevaluationresult.true_anomalies:
                true_anomaly = true_anomaly_tuple[0]

                anomaly_list.append((true_anomaly.anomaly_type, true_anomaly.score, True))

            for false_anomaly_tuple in logevaluationresult.false_anomalies:
                false_anomaly = false_anomaly_tuple[0]
                anomaly_list.append((false_anomaly.anomaly_type, false_anomaly.score,False))

        return anomaly_list

    @staticmethod
    def get_positives(anomaly_list):
        true_anomalies = [anomaly for anomaly in anomaly_list if anomaly[2]==True]
        false_anomalies = [anomaly for anomaly in anomaly_list if anomaly[2]==False]

        return len(true_anomalies), len(false_anomalies)

    @staticmethod
    def get_precision(anomaly_list):

        if anomaly_list:
            true_anomalies = [anomaly for anomaly in anomaly_list if anomaly[2]==True]
            false_anomalies = [anomaly for anomaly in anomaly_list if anomaly[2]==False]

            return len(true_anomalies)/(len(true_anomalies) + len(false_anomalies))
        else:
            return -1

    def split_anomalies_into_chunks(self, increment = 0.05):
        chunks = {}
        actual_increment = 0

        # 1. Create anomaly dict
        while actual_increment<1:
            chunks[actual_increment]=[]
            actual_increment=round(actual_increment+increment,2)

        print(chunks)
        # 2. Fill up dict


        for anomaly in self.anomaly_list:
            score = anomaly[1]
            
            for key in chunks:
                if score<key:
                    chunks[round(key-increment,2)].append(anomaly)
                    break            
            else:
                chunks[max(chunks.keys())].append(anomaly)


        sum_anomalies = 0
        for anomalies in chunks.values():
            sum_anomalies+=len(anomalies)

        print(f'sum_anomalies: {sum_anomalies}')

        #print(chunks[0.25])
        #print(max(chunks.keys()))

        # 3. Calculate precision per chunk
        chunks_precision = {}

        for key, anomaly_list in chunks.items():
            chunks_precision[key] = self.get_precision(anomaly_list)

        # 4. Calculate cumulative precision
        
        cumulative_precision = {}
        current_increment = max(chunks.keys()) #0.95
        current_anomaly_list = []

        while current_increment in chunks_precision.keys():
            print(current_increment)

            for anomaly in chunks[current_increment]:
                current_anomaly_list.append(anomaly)

            print(f'Length of anomaly list: {len(current_anomaly_list)}')

            cumulative_precision[current_increment] = self.get_precision(current_anomaly_list)
            current_increment=round(current_increment-increment,2)   

                

        print(cumulative_precision)
        return chunks_precision, cumulative_precision

    @staticmethod  
    def draw_conf_prec_graph(chunks_precision):
        plt.scatter(list(chunks_precision.keys()),list(chunks_precision.values()))
        plt.xlim(1.1,0)
        #plt.ylim(0,1.1)
        plt.show()

"""

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
"""

if __name__ == '__main__':
    anomaly_classifier = AnomalyClassifier()   
    chunks_precision, cumulative_precision = anomaly_classifier.split_anomalies_into_chunks()

    anomaly_classifier.draw_conf_prec_graph(chunks_precision)
    anomaly_classifier.draw_conf_prec_graph(cumulative_precision)

    #print(anomaly_classifier.get_precision(anomaly_classifier.anomaly_list))
    #print(anomaly_classifier.get_positives(anomaly_classifier.anomaly_list))




