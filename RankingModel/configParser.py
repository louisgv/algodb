import json
from BinaryNBModel import BinaryNBModel
from RankingModel import RankingModel
from ThresholdModel import ThresholdModel

modelMap = {
    'BinaryNBModel': BinaryNBModel,
    'RankingModel': RankingModel,
    'ThresholdModel': ThresholdModel
}

defaultConfig = {
    "balanced_train": False,
    "balanced_test": False,
    "num_splits": 5,
    "workflow": []
}

def read_config(filename, override):
    config = defaultConfig.copy()
    # load config from file
    config.update(json.load(open(filename)))
    # inject override
    config.update(override)
    assert isinstance(config['workflow'], list)
    return config

def get_models(config):
    return [modelMap[model] for model in config['workflow']]

def load_models(config, extract_features, all_algos):
    def create_model(config):
        model = config['model']
        params = config.copy()
        del params['model']
        return modelMap[model](extract_features, all_algos, **params)
    return map(create_model, config['workflow'])
