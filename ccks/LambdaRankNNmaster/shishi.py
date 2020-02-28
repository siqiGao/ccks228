import numpy as np
from LambdaRankNN import LambdaRankNN

def lambdarank(entity_info,flag):
    if flag == 0:
        X = []
        print(entity_info)
        for i in entity_info:
            X.append(i[2:])
        X = np.array(X)
        print(X)
        ranker = LambdaRankNN(input_size=X.shape[1], hidden_layer_sizes=(16,8,), activation=('relu', 'relu',), solver='adam')
        ranker.model.load_weights('LambdaRankNNmaster\Examples\entity_select225.h5')
        y_pred = ranker.predict(X)
        return y_pred
    else:
        X = []
        print(entity_info)
        for i in entity_info:
            X.append(i[4:])
        X = np.array(X)
        print(X)
        ranker = LambdaRankNN(input_size=X.shape[1], hidden_layer_sizes=(16,8,), activation=('relu', 'relu',), solver='adam')
        ranker.model.load_weights('LambdaRankNNmaster\Examples\drelation_select22515.h5')
        y_pred = ranker.predict(X)
        return y_pred

