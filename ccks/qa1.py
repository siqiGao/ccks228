# -*- coding: utf-8 -*-
import ccksNeo
import jieba
import serviceWord2vec
import re
import LambdaRankNNmaster.shishi as LambdaRank
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer
from nltk.metrics.distance import jaccard_distance
import difflib
import config

model = config.w2v_model

# 指称识别
def segmentsentence(sentence):
    segmentor = Segmentor()
    postagger = Postagger()
    parser = Parser()
    recognizer = NamedEntityRecognizer()

    segmentor.load("./ltpdata/ltp_data_v3.4.0/cws.model")
    postagger.load("./ltpdata/ltp_data_v3.4.0/pos.model")
    # parser.load("./ltpdata/ltp_data_v3.4.0/parser.model")
    recognizer.load("./ltpdata/ltp_data_v3.4.0/ner.model")
    #############
    word_list = segmentor.segment(sentence)
    postags_list = postagger.postag(word_list)
    nertags = recognizer.recognize(word_list, postags_list)
    ############
    for word, ntag in zip(word_list, nertags):
        if ntag == 'Nh':
            entity_list.append(word)
    print(" ".join(word_list))
    print(' '.join(nertags))
    ############
    segmentor.release()
    postagger.release()
    # parser.release()
    recognizer.release()
    return word_list


def entityRecognize(word_list):
    for word in word_list:
        entity = ""
        finalentity = ""
        for temp_entity in word_list[word_list.index(word):]:
            entity = entity + temp_entity
            if len(entity) > 1:
                # print(entity)
                print(1)
                same_name_entity_list = ccksNeo.get_entity_list_by_name(entity)
                if len(same_name_entity_list) >= 1:
                    entity_list.append(entity)
    # print(entity_list)
    for entity1 in entity_list:  # 如果短的指称被长的指称包含，检测短指称的一度关系名
        for entity2 in entity_list:
            if entity1 != entity2 and entity1 in entity2:
                temp_list = sentence.replace(entity1, "")
                segmentor1 = Segmentor()
                segmentor1.load("./ltpdata/ltp_data_v3.4.0/cws.model")
                temp_list = segmentor1.segment(temp_list)
                segmentor1.release()
                print(2)
                same_name_entity_list = ccksNeo.get_entity_list_by_name(entity1)
                flag = 0
                for entitydict in same_name_entity_list:
                    print(entitydict, "用id查")
                    print(3)
                    relations = ccksNeo.get_related_entities_by_neoid(entitydict['id'])
                    # print(relations)
                    for relation in relations:  # 除掉实体的剩余句子
                        # print(temp_list, relation['name'])
                        '''
                        segmentor2 = Segmentor()
                        segmentor2.load("./ltpdata/ltp_data_v3.4.0/cws.model")
                        #print("测试处", relation['name'])
                        relation_list = segmentor2.segment(relation['name'])
                        segmentor2.release()
                        '''
                        # print(temp_list)
                        # print(relation_list)
                        score = serviceWord2vec.get_similarity(temp_list, list(jieba.cut(relation['name'])))
                        # print("测试分数", score)
                        if score > 0.2:
                            flag = 1
                if flag == 0 and entity1 in entity_list:
                    # print(entity_list)
                    # print(entity1)
                    entity_list.remove(entity1)
    print("entity_list",entity_list)


# 实体链接
def entityLink(entity_list, question):  # (通过实体名找到数据库中的各实体并通过评分策略找到中心实体)
    scores = []
    allentity_info = []

    for name in entity_list:
        print(4)
        entity_total = ccksNeo.get_entity_list_by_name(name)  # 指称的所有实体
        print(entity_total)
        temp = question.replace(name, "")  # 去掉指称的剩余句子
        # print(temp)
        segmentor1 = Segmentor()
        segmentor1.load("./ltpdata/ltp_data_v3.4.0/cws.model")
        temp = list(segmentor1.segment(temp))
        # print(temp)   #剩余句子分词
        segmentor1.release()

        for entity in entity_total:
            # id = q_id
            relation_list = []
            entity_Id = entity['id']
            # print("用id")
            print(5)
            relations = ccksNeo.get_related_entities_by_neoid(entity['id'])
            print(relations)
            max_relation_score = 0
            for relation in relations:  # 不同的关系，可能有类别相同的关系

                relation_list.append(relation['name'])
                '''
                segmentor2 = Segmentor()
                segmentor2.load("./ltpdata/ltp_data_v3.4.0/cws.model")
                temp2 = list(segmentor2.segment(relation['name']))
                segmentor2.release()
                '''
                score = serviceWord2vec.get_similarity(temp, list(jieba.cut(relation['name'])))  # 只要实体关系和句子沾边
                # print(temp, temp2, score)
                if score > max_relation_score:
                    max_relation_score = score

            link_relation_num = len(relation_list)
            relation_list_type = set(relation_list)
            link_relation_type_num = len(relation_list_type)

            # print(question)
            if "《" + name + "》" in question or "\"" + name + "\"" in question or "“" + name + "”" in question:
                be_included = 1
            else:
                be_included = 0
            relative_position = question.find(name) / len(question)
            have_quesition_word = 0
            # question_word_num = 0
            min_distance = 100
            for question_word in question_words:
                if question_word in question:
                    have_quesition_word = 1
                    # question_word_num = question_word_num+1
                    if min_distance > abs(question.find(question_word) - question.find(name)):
                        min_distance = abs(question.find(question_word) - question.find(name))
            have_alpha_or_digit = 0
            pattern1 = re.compile('[0-9]+')
            pattern2 = re.compile('[a-z]+')
            pattern3 = re.compile('[A-Z]+')
            match1 = pattern1.findall(name)
            match2 = pattern2.findall(name)
            match3 = pattern3.findall(name)
            if match1 or match2 or match3:
                have_alpha_or_digit = 1
            entity_length = len(name)
            '''
            if name == c_name:
                is_correct_name =1
            else:
                is_correct_name =0


            if entity['keyId'] == c_keyid:
                is_correct_entity = 1
            else:
                is_correct_entity = 0

            print(q_id, entity_keyId, one_relation, link_relation_num, link_relation_type_num, be_included, relative_position, have_quesition_word, min_distance,
                  have_alpha_or_digit, entity_length, is_correct_entity)

            sentence = q_id+'  '+entity_keyId+'  '+str(one_relation)+'  '+str(link_relation_num)+'  '+str(link_relation_type_num)+'  '+str(be_included)+'  '+str(relative_position)+'  '+str(have_quesition_word)+'  '+str(min_distance)+'  '+str(have_alpha_or_digit)+'  '+str(entity_length)+'  '+str(is_correct_entity)+'\n'
            p = open("../NLPCC_KBQA/nlpcc-iccpol-2016.kbqa.training-data_processtry2.txt", 'a', encoding="utf-8")
            p.writelines(sentence)
            p.close()
            '''
            entity_info = [name, entity_Id, max_relation_score, link_relation_num, link_relation_type_num, be_included,
                           relative_position, have_quesition_word, min_distance,
                           have_alpha_or_digit, entity_length]
            allentity_info.append(entity_info)

    # print(allentity_info)
    return allentity_info
    '''
        frequency = len(entity_total)  #实体频率
        allentity = allentity + entity_total

    relation = []
    for entitydict in entity_total:
        relations = ccksNeo.get_related_entities_by_id(entitydict['neoId'])
        print(relations)
        for relationname in relations:
            relation.append(relationname['name'])
    set(relation)
    relationfrequency = len(relation)
    print(frequency, relationfrequency)
    score = frequency + relationfrequency
    scores.append(score)
'''


def entity_sort(entity_info):  # 返回得分最大的两个实体id。[name, entity_Id, one_relation, link_relation_num,
    # link_relation_type_num, be_included, relative_position, have_quesition_word, min_distance,have_alpha_or_digit, entity_length]
    result = []
    if len(entity_info) == 1:  # 返回name和keyid
        result = entity_info[:2]
        return result
    else:
        result = []
        flag = 0
        entity_scores = LambdaRank.lambdarank(entity_info, flag)
        print(entity_scores)
        temp_score = entity_scores

        a = sorted(temp_score, key=lambda x: x * 1000 if x < 0 else x, reverse=True)
        print(a)
        res = [idx for idx, i in enumerate(entity_scores) if i == a[0]]
        print(res)
        for i in res:
            print(i)
            temp = []
            temp = entity_info[i][:2]
            result.append(temp)

        res = [idx for idx, i in enumerate(entity_scores) if i == a[1]]
        for j in res:
            print(j)
            temp = []
            temp = entity_info[j][:2]
            result.append(temp)
        return result


##########################################
def get_realtion_info(relation_candidate, remain_sentence):  # [name, relation, target_entity, target_entity_keyid]
    # temp_relations = ccksNeo.get_entity_info_by_keyid(entity_keyid)  #该实体的信息
    # 实体名，路径，目标实体
    # print(temp_relations)
    relation_info = []
    for candidate in relation_candidate:
        # for key, value in temp_relations.items():  #路径名，目标实体
        segmentor1 = Segmentor()
        segmentor1.load("./ltpdata/ltp_data_v3.4.0/cws.model")

        temp = list(segmentor1.segment(remain_sentence))
        segmentor1.release()
        guanxideci = jieba.cut(candidate[0])
        for word in guanxideci:
            if word in model and word in temp:
                temp.remove(word)
        '''
        segmentor2 = Segmentor()
        segmentor2.load("./ltpdata/ltp_data_v3.4.0/cws.model")
        temp2 = list(segmentor2.segment(candidate[1]))
        segmentor2.release()
        '''
        ##################jaccard
        temp2 = [candidate[1]]
        set1 = set(temp)
        set2 = set(temp2)
        jaccard = jaccard_distance(set1, set2)
        edit = difflib.SequenceMatcher(None, question, candidate[1]).ratio()
        print(temp, temp2)
        w2v = serviceWord2vec.get_similarity(temp, list(jieba.cut(candidate[1])))
        '''

        if key == c_relation_name:
            is_correct = 1
        else:
            is_correct = 0
        '''
        #
        relation_info.append([candidate[0], candidate[1], candidate[2], candidate[3], jaccard, edit, w2v])
        # 实体，路径名，目标实体，jaccard距离，编辑距离，向量相似度
    # print(relation_info)
    return relation_info
    '''
    print(id,  entity_keyid, key, jaccard, edit, w2v, is_correct)
    sentence = str(id) + "  " + str(entity_keyid) + "  " +str(key)+ "  "+ str(jaccard)+ "  " +str(edit)+"  " +str(w2v)+"  " +str(is_correct)+'\n'
    w = open("../NLPCC_KBQA/nlpcc-iccpol-2016.kbqa.training-data_process_entity_info.txt", 'a', encoding="utf-8")
    w.writelines(sentence)
    w.close()
    '''


#################################################
def relation_sort(relation_info):  # [entity_name, relation, target_entity, target_entity_keyid, jaccard, edit, w2v]
    print(relation_info)
    if len(relation_info) == 1:
        return relation_info
    else:
        temp = []
        flag = 1
        relation_scores = LambdaRank.lambdarank(relation_info, flag)
        print(relation_scores)
        temp_score = relation_scores
        # entity_scores.sort()
        a = sorted(temp_score, key=lambda x: x * 1000 if x < 0 else x, reverse=True)
        print(a)

        result = []
        res = [idx for idx, i in enumerate(relation_scores) if i == a[0]]
        for i in res:
            # print(i)
            temp = []
            temp = relation_info[i]
            result.append(temp)
        '''
        res = [idx for idx, i in enumerate(relation_scores) if i == a[1]]
        for j in res:
            # print(i)
            temp = []
            temp = relation_info[j]
            result.append(temp)
        '''
        print(result)
        return result


######################三种问题模板
def template(using_entity):  # 使用实体id，传进来的是[name , keyid]
    print(using_entity)
    # template1
    query_candidates = []
    relations1 = []
    relations2 = []
    relations3 = []
    for e in using_entity:
        print(6)
        temp_relations = ccksNeo.lalala(e[1])  # 该实体的所有relation信息
        print("temp_relations:", temp_relations)  # [relation, target_entity, target_entity_id]
        for i in temp_relations:
            triple = [e[0], i[0], i[1], i[2]]
            relations1.append(triple)  # 所有实体的信息三元组[name, relation, target_entity ,target_entity_keyid]
    print(relations1)
    remain_sentence = question.replace(relations1[0][0], "")
    relation_info = get_realtion_info(relations1, remain_sentence)
    result1 = relation_sort(relation_info)
    result_candidates = result1
    print(result1)
    #return result1
    #result1 = relation_sort(relation_info)[:2]  # 只有两个候选
    # print("result1:", result1)
    #####  选择距离实体最近的关系
    '''
    if result1[0][1] == result1[1][1]:
        if result1[0][1] in remain_sentence and result1[1][1] in remain_sentence:
            distance1 = abs(question.find(result1[0][1]) - question.find(result1[0][0]))
            distance2 = abs(question.find(result1[1][1]) - question.find(result1[1][0]))
            if distance1 > distance2:
                result_candidate = result1[1]
                print(result1[1])
            else:
                result_candidate = result1[0]
                print(result1[0])
        elif result1[0][1] not in remain_sentence and result1[1][1] in remain_sentence:
            result_candidate = result1[1]
            print(result1[1])
        else:
            result_candidate = result1[0]
            print(result1[0])
    else:
        result_candidate = result1[0]  # [name, relation, target_entity ,target_entity_keyid]
        print(result1[0])
    '''
    # template2
    #for result_candidate in result_candidates:
    print(relations1)
    for relation in relations1:
        owl_relations2 = ccksNeo.lalala(relation[3])
        for i in owl_relations2:
            triple = [relation[1], i[0], i[1], i[2]]  #对第二跳来说实体是关系名
            relations2.append(triple)  # 二度子图所有实体的信息三元组[name, relation, target_entity ,target_entity_keyid]
    print(relations2)
    relation_info = get_realtion_info(relations2, remain_sentence)
    result2 = relation_sort(relation_info)
    print(result2)
    print(result1, result2)
    return result1,result2


    '''
    #template2
    for relation in temp_relations:
        query_candidates.append([relation['target_name'], relation['target_neoId']])
    print(query_candidates)
    for candidate in query_candidates:
        relations2 = relations2 + owlNeo4j.get_related_entities_by_id(candidate[1])
    print(relations2)


    #template3
        for e1 in entity_list:
            for e2 in entity_list[entity_list.index(e1):]:
                if e1 not in e2 and e2 not in e1:
                    rm_list1 = []
                    rm_list2 = []
                    e1_relation = []
                    e2_relation = []
                    e1_entity_list = ccksNeo.get_entity_list_by_name(e1)
                    for entity in e1_entity_list:
                        e1_relation = e1_relation + ccksNeo.get_related_entities_by_id(entity['neoId'])
                        for relation in e1_relation:
                            rm_list1.append([relation['name'], relation['target_name'], relation['target_neoId']])
                    e2_entity_list = ccksNeo.get_entity_list_by_name(e2)
                    for entity in e2_entity_list:
                        e2_relation = e2_relation + ccksNeo.get_related_entities_by_id(entity['neoId'])
                        for relation in e2_relation:
                            rm_list2.append([relation['name'], relation['target_name'], relation['target_neoId']])
                    #求rm交集
                    rm_intersect = [x for x in rm_list1 if x in rm_list2]
                    for rm in rm_intersect:
                        query_candidates.append([rm[1], rm[2]])
                        relations3 = relations3 + ccksNeo.get_related_entities_by_id(rm[2])
'''



entity_list = []  #筛选出来的指称
allentity = []  #实体
word_list = []
'''
sentence = "西湖景区的湖中二塔是？"
word_list = segmentsentence(sentence)
word_list = list(word_list)  #分词后的原始指称
entityRecognize(word_list)
print(entity_list)
entityLink(entity_list)
#template(allentity)
'''

p = open("onehop_226.txt", 'r+', encoding="utf-8")

for line in p:
    using_entity = []
    index1 = line.find("|||")
    index2 = line[index1+4:].find("|||")
    index3 = line[index1+index2+8:].find("|||")
    index4 = line[index1+index2+index3+12:].find("|||")
    print(index1,index2,index3,index4)
    question_id = line[:index1]
    question = line[index1+3:index2+index1+4]
    shiti1 = line[index1+index2+7:index3+index2+index1+8]
    index11 = shiti1.find('|')
    using_entity.append([shiti1[:index11],shiti1[index11+1:]])
    shiti2 = line[index1+index2+index3+11:index4 + index3 + index2 + index1 + 12]
    index22 = shiti2.find('|')
    using_entity.append([shiti2[:index22],shiti2[index22+1:]])
    print(question_id,question, using_entity)
    sentence = question
    question_words = ["谁", "何", "哪", "什么", "哪儿", "哪里", "几时", "几", "多少",
                      "怎", "怎么", "怎的", "怎样", "怎么样", "怎么着", "如何", "为什么",
                      "吗", "呢", "吧", "啊", ]
    '''
    #question = "光武中兴说的是哪一位皇帝"
    entity_list = []  # 筛选出来的指称
    # allentity = []  # 实体
    entity_info = []
    using_entity = []
    sentence = question
    word_list = segmentsentence(sentence)
    word_list = list(word_list)  # 分词后的原始指称
    print(word_list)
    entityRecognize(word_list)  # 这里召回的是指称
    print(entity_list)
    entity_info = entityLink(entity_list, question)  # 提取实体用于排序的信息
    using_entity = entity_sort(entity_info)  # 实体排序的结果（top2），得到name和id
    print(using_entity)
    '''
    result1,result2 = template(using_entity)  # 模板里选出relation
    daan1 = ""
    daan2 = ""
    for result in result1:
        daan1 = daan1 + str(result[0])+'|'+str(result[1])+'|'+str(result[2]) + '||'

    for result in result2:
        daan2 = daan2 + str(result[0])+'|'+str(result[1])+'|'+str(result[2]) + '||'
    q = open("relation228.txt", 'a', encoding="utf-8")
    q.writelines(question_id + '|||'+ question + '|||'+ daan1 +'|||'+daan2+'\n')
'''
q = open("../NLPCC_KBQA/nlpcc-iccpol-2016.kbqa.training-data_process.txt", 'r', encoding="utf-8")

for line in q:    #对每一个问句提出来进行分析和处理
    q_id = line.split("  ")[0]
    question = line.split("  ")[1]
    c_name = line.split("  ")[2]
    c_relation = line.split("  ")[3]
    c_target = line.split("  ")[4]
    #print(q_id, question, c_name, c_relation, c_target[:-1])
    c_keyid = ccksNeo.get_keyid_by_nrm(c_name, c_relation, c_target[:-1])

    if c_keyid:   #检索问题的实体-路径-答案是否所有信息都在数据库里，没有的话这个问句不用
        entity_list = []  # 筛选出来的指称
        #allentity = []  # 实体
        sentence = question
        word_list = segmentsentence(sentence)
        word_list = list(word_list)  # 分词后的原始指称
        print(word_list)
        entityRecognize(word_list)  #这里召回的是指称
        print(entity_list)

        entityLink(entity_list, question, q_id, c_keyid)
'''
