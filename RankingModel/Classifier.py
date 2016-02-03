# # for task data
# from cassandra.cluster import Cluster

# for algorithm
from elasticsearch import Elasticsearch

# for training set labels
import redis

# using support vector regression: features -> ranking score
from sklearn import svm
clf = svm.LinearSVR()

# for randomly sampling negative training example
import random

def train():
    CORRESPONDING = 1.0
    NON_CORRESPONDING = 0.0

    # for task names and labels
    rd = redis.StrictRedis(host='localhost', port=6379, db=0)
    # for algo names and data
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    # get all task names in rosettacode
    task_names = rd.hkeys('rosettacode-label-algoname')
    # get all algo names in elasticsearch algorithm table
    query = {
        "query": {
            "match_all" : {}
        }
    }
    res = es.search(index='throwtable', doc_type='algorithm', body=query)
    algo_names = [entry['name'] for entry in res['hits']]

    # debugging
    print '# of task_names:', len(task_names)
    print '# of algo_names:', len(algo_names)

    # feature vector
    feature_vector = list()
    # score vector
    score_vector = list()

    for task_name in task_names:
        algo_name = rd.hget('rosettacode-label-algoname', task_name)
        # now only train on tasks that are algorithms, and have wiki pages
        if not rd.sismember('rosettacode-label-isalgo', task_name) \
            or len(algo_name) == 0:
            continue

        # TODO: not using algorithm's data for now
        # # get algorithm's data from our algo db
        # algo = es.get(index='throwtable', doc_type='algorithm',
        #     id=normalize(algo_name), ignore=404)
        # if not result['found']:
        #     print 'corresponding algo is not in elasticsearch'
        #     continue

        # positive:negative = 1:1
        # positive training example
        feature_vector.extend(mock_extractor(task_name, algo_name))
        score_vector.extend(CORRESPONDING)
        # negative training example
        random_algo = random.choice(algo_names)
        while (random_algo == algo_name): # until we get a negative example
            random_algo = random.choice(algo_names)
        feature_vector.extend(mock_extractor(task_name, random_algo))
        score_vector.extend(NON_CORRESPONDING)

    # train
    clf.fit(feature_vector, score_vector)

# samples_features = a list of features, size = # of samples * # of features
# returns a list of
def classify(samples_features):
    return predict(samples_features)
