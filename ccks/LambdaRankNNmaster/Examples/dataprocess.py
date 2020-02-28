import numpy as np
np.set_printoptions(threshold=np.inf)
from LambdaRankNN import LambdaRankNN, RankNetNN
X = []
y = []
qid = []

p = open("nlpcc-iccpol-2016.kbqa.training-data_process_mention.txt", 'r', encoding="utf-8-sig")

for line in p:
    line = line.encode('utf-8').decode('utf-8-sig')
    data = line.split('  ')
    temp = data[2:-1]
    temp = [float(x) for x in temp]
    print(temp)
    process_data = temp
    flag = int(data[-1][0])
    id = int(data[0])
    #print(process_data, flag, id)
    X.append(process_data)
    y.append(flag)
    qid.append(id)
print(X)
X = np.array(X)
y = np.array(y)
qid = np.array(qid)
print(y, qid)


ranker = LambdaRankNN(input_size=X.shape[1], hidden_layer_sizes=(16,8,), activation=('relu', 'relu',), solver='adam')
ranker.fit(X, y, qid, epochs=5)
#ranker.model.save_weights('mention_select__weights.h5')
y_pred = ranker.predict(X)
print(y_pred)
ranker.evaluate(X, y, qid, eval_at=2)
