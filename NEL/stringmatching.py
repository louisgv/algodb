import os
import string
import unicodecsv as csv
from nltk import ngrams
import math


def load_data(algo_file_name, test_file_folder):
    with open(algo_file_name, "rb") as f:
        reader = csv.reader(f)
        algo_names = [row[0].lower() for row in reader]

    corpus = []
    file_names = []
    for fname in os.listdir(test_file_folder):
        file_names.append(fname)
        with open(os.path.join(test_file_folder, fname), "r") as f:
            corpus.append(f.read().lower())
    return algo_names, corpus, file_names


# N-gram string matching
def string_match(algo_names, corpus,  file_names):
    idx = 0
    detected = {}
    algo_total_frequency = {}
    for doc in corpus:
        algo_doc_frequency = {}
        for algo in algo_names:
            num_counts = string.count(doc, algo)
            if num_counts != 0:
                algo_doc_frequency[algo] = num_counts
        for name, freq in algo_doc_frequency.items():
            if name not in algo_total_frequency:
                algo_total_frequency[name] = 0
            algo_total_frequency[name] += 1
        detected[file_names[idx]] = algo_doc_frequency
        idx += 1        
    tf_idf(detected, algo_total_frequency)
    return detected


def tf_idf(doc_freq, total_freq):
    for doc, algos_found in doc_freq.items():
        for algo, freq in algos_found.items():
            doc_freq[doc][algo] = freq * math.log(1.0 * len(doc_freq) / total_freq[algo])

def run():
    # Read algo names and get test doc corpus
    algo_file_name = "algolist.csv"
    test_file_folder = "testDocs"

    algo_names, corpus, file_names = load_data(algo_file_name, test_file_folder)
    detected_algos = string_match(algo_names, corpus,  file_names)
    for doc, algos_found in detected_algos.items():
        print("expected: " + doc, "got: " + str(algos_found))

run()
