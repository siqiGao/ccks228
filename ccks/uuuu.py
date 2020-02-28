# coding=utf-8
import base64
import requests
import numpy as np
from py2neo import Graph
from pandas import DataFrame
'''
bbs = str(base64.b64decode('bmVvNGo6MTIzNDU2'), "utf-8")
print(bbs) # 解码
'''
'''
graph1 = Graph("http://10.1.1.28:7474", username="neo4j", password="123456")
keyid = '2271/4818353'
#statement = "match (n:Instance)-[r]->(m:Instance) where n.keyId = \"" + str(keyid) + "\" return type(r), m.name, m.keyId"
statement = "match (n:Instance) where n.name= \""+"红楼梦"+"\" return n"
list1 = graph1.run(statement).data()
#print(list1)

result = []
for element in list1:  #子（实体）
    sub_result = {}
    sub_row = []
    for key, values in element.items():  #返回来的结果类型如id，type，n等
        if isinstance(values, dict):
            sub_sub_result = {}
            for i, j in values.items():
                sub_sub_result[i] = j
            sub_row.append(sub_sub_result)
        else:
            sub_row.append(values)
    sub_result['row'] = sub_row
    result.append(sub_result)
print(result)

entity = []
if len(result) != 0:
    for i in result:
        entity.append(i["row"])
print(entity)
'''
'''
graph1 = Graph("http://10.1.1.30:9700/browser/", username="neo4j", password="123456")
#statement = "match (n:Instance)-[r]->(m:Instance) where n.name = \"+"龙卷风\"+"  return n"
statement = "match (n:Instance)-[r]->(m:Instance) where n.id=\""+str(10713688)+"\" return r.value,m.name,m.id"
print(statement)
list1 = graph1.run(statement).data()
print(list1)

result = []
for element in list1:  # 子（实体）
    sub_result = {}
    sub_row = []
    for key, values in element.items():  # 返回来的结果类型如id，type，n等
        if isinstance(values, dict):
            sub_sub_result = {}
            for i, j in values.items():
                sub_sub_result[i] = j
            sub_row.append(sub_sub_result)
        else:
            sub_row.append(values)
    sub_result['row'] = sub_row
    result.append(sub_result)
print(result)
'''
'''
statement = "match (n:Instance)-[r]->(m:Instance) where id(n) =" + str(neoid) + " return type(r), m.label, m.name, id(m)"
related_entities = []
result = execute(statement)


for data in result:
    related_entities.append({'name': data['row'][0], 'target_label': data['row'][1], 'target_name': data['row'][2],
                             'target_neoId': data['row'][3]})
return related_entities
'''

'''
from pyltp import SentenceSplitter,Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller
temp_list = "汉字"
segmentor1 = Segmentor()
segmentor1.load("./ltpdata/ltp_data_v3.4.0/cws.model")
temp_list = segmentor1.segment(temp_list)
segmentor1.release()
print([temp_list])
for i in temp_list:
    print(i)
'''
a = ['爸爸']
b = ['爸爸','爸爸','sasa']
for i in a:
    if i in b:
        b.remove(i)
print(b)