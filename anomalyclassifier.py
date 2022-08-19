"""
This file is part of the repository belonging to the Master Thesis of Gusztáv Megyesi - MN 1526252
Title: Incorporation of Commonsense Knowledge Resources for Semantic Anomaly Detection in Process Mining
Submitted to the Data and Web Science Group - Prof. Dr. Han van der Aa - University of Mannheim in August 2022
"""

import pickle, sys
from knowledgebase.knowledgerecord import Observation
import matplotlib.pyplot as plt

class AnomalyClassifier:

    chunk_increment = 0.05
    #Load raw results of previously executed anomaly detection - there is no need to run it anymore:
    ser_file = 'output/05_AnomalyClassification/KBExtended/raw_results/simmode_SimMode.EQUALkbheuristics_Trueanomalyclassification_True.ser'
    #ser_file = 'output/05_AnomalyClassification/KBExtended/raw_results/simmode_SimMode.SYNONYMkbheuristics_Trueanomalyclassification_True.ser'
    #ser_file = 'output/05_AnomalyClassification/KBExtended/raw_results/simmode_SimMode.SEMANTICSIMsimthres_0.5kbheuristics_Trueanomalyclassification_True.ser'




    def __init__(self):
        self.log_result_map = pickle.load(open(self.ser_file, 'rb')).log_result_map
        self.anomaly_list = self.get_all_anomalies()

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

    # Get true and false positive count of a list of anomalies
    @staticmethod
    def get_positives(anomaly_list):
        true_anomalies = [anomaly for anomaly in anomaly_list if anomaly[2]==True]
        false_anomalies = [anomaly for anomaly in anomaly_list if anomaly[2]==False]

        return len(true_anomalies), len(false_anomalies)

    # Get precision of anomalies of a list of anomalies
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

        # 3. Calculate precision per chunk
        chunks_precision = {}

        for key, anomaly_list in chunks.items():
            chunks_precision[key] = self.get_precision(anomaly_list)

        # 4. Calculate cumulative precision
        cumulative_precision = {}
        current_increment = max(chunks.keys()) #0.95
        current_anomaly_list = []
        anomaly_numbers_direct = {}
        anomaly_numbers_cumulative = {}

        while current_increment in chunks_precision.keys():
            anomaly_counter=0
            for anomaly in chunks[current_increment]:
                current_anomaly_list.append(anomaly)
                anomaly_counter+=1

            anomaly_numbers_direct[current_increment]=anomaly_counter
            anomaly_numbers_cumulative[current_increment]=len(current_anomaly_list)

            cumulative_precision[current_increment] = self.get_precision(current_anomaly_list)
            current_increment=round(current_increment-increment,2)

        print(f'Anomalies in chunk: {anomaly_numbers_direct}')
        print(f'Anomalies cumulatively in chunk: {anomaly_numbers_cumulative}')
        print(f'Actual precision per chunk: {chunks_precision}')
        print(f'Cumulative precision per chunk: {cumulative_precision}')

        return chunks_precision, cumulative_precision, anomaly_numbers_direct, anomaly_numbers_cumulative

    @staticmethod
    def draw_conf_prec_graph(chunks_precision, title, anomaly_numbers):

        plt.scatter(list(chunks_precision.keys()),list(chunks_precision.values())) #,s=list(anomaly_numbers.values()))
        plt.xlim(1.05,0)
        plt.ylim(0.6,1.05)
        plt.title(title, fontdict=None, loc='center', pad=None, fontsize='medium')
        plt.show()


if __name__ == '__main__':
    anomaly_classifier = AnomalyClassifier()
    chunks_precision, cumulative_precision, anomaly_numbers_direct, anomaly_numbers_cumulative = anomaly_classifier.split_anomalies_into_chunks()

    # Draw plots - might be required to replace EQUAL/SYNYONM in the title
    anomaly_classifier.draw_conf_prec_graph(chunks_precision, 'Anomaly Score and Precision - SEM 0.5 - Actual Precision per chunk', anomaly_numbers_direct)
    anomaly_classifier.draw_conf_prec_graph(cumulative_precision, 'Anomaly Score and Precision - SEM 0.5 - Cumulative Precision per chunk' , anomaly_numbers_cumulative)
