#!/usr/bin/env python3
#coding: utf-8

#基于训练好的词向量模型进行聚类
#聚类采用Kmeans算法
import math
import re
import json
import jieba
import numpy as np
from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from collections import defaultdict

#输入模型文件路径
#加载训练好的模型
def load_word2vec_model(path):
    model = Word2Vec.load(path)
    return model

def load_sentence(path):
    sentences = set()
    with open(path, encoding="utf8") as f:
        for line in f:
            sentence = line.strip()
            sentences.add(" ".join(jieba.cut(sentence)))
    print("获取句子数量：", len(sentences))
    return sentences

#将文本向量化
def sentences_to_vectors(sentences, model):
    vectors = []
    for sentence in sentences:
        words = sentence.split()  #sentence是分好词的，空格分开
        vector = np.zeros(model.vector_size)
        #所有词的向量相加求平均，作为句子向量
        for word in words:
            try:
                vector += model.wv[word]
            except KeyError:
                #部分词在训练中未出现，用全0向量代替
                vector += np.zeros(model.vector_size)
        vectors.append(vector / len(words))
    return np.array(vectors)

def cosine_distance(vec1, vec2):
    dot_product = np.dot(np.array(vec1), np.array(vec2))
    norm_vec1 = np.linalg.norm(np.array(vec1))
    norm_vec2 = np.linalg.norm(np.array(vec2))
    return 1 - dot_product / (norm_vec1 * norm_vec2)

def get_low_n_keys(dictionary, n):
    # 对字典的键值对按照值进行降序排序，排序依据是 lambda 函数指定的取每个键值对中的值（item[1]）
    sorted_items = sorted(dictionary.items(), key=lambda item: item[1])
    # 提取排序后的前 N 个键值对
    top_n_items = sorted_items[:n]
    # 只取前 N 个键值对中的键，组成一个列表返回
    return [item[0] for item in top_n_items]


def main():
    model = load_word2vec_model(r"F:\NLP\code\study\week5\week5 词向量及文本向量\model.w2v") #加载词向量模型
    sentences = load_sentence("titles.txt")  #加载所有标题
    vectors = sentences_to_vectors(sentences, model)   #将所有标题向量化

    n_clusters = int(math.sqrt(len(sentences)))  #指定聚类数量
    print("指定聚类数量：", n_clusters)
    # kmeans = KMeans(n_clusters)  #定义一个kmeans计算类
    kmeans = KMeans(n_clusters, n_init=10, random_state=0)  # 定义一个kmeans计算类
    kmeans.fit(vectors)          #进行聚类计算

    sentence_label_dict = defaultdict(list)
    for sentence, label in zip(sentences, kmeans.labels_):  #取出句子和标签
        sentence_label_dict[label].append(sentence)         #同标签的放到一起

    label_list={}
    for label,sentences in sentence_label_dict.items():
        vetors_1 = sentences_to_vectors(sentences, model)
        sum=0
        for vetor in vetors_1:
            sum+=cosine_distance(vetor,kmeans.cluster_centers_[label])
        label_list[label]=sum/len(sentences)

    print(label_list)

    top_keys = get_low_n_keys(label_list, 5)
    for label in top_keys:
        print("cluster %s :" % label)
        list1 = sentence_label_dict.get(label)
        for i in range(min(10,len(list1))):  # 随便打印几个，太多了看不过来
            print(list1[i].replace(" ", ""))
        print("---------")






    # for label, sentences in sentence_label_dict.items():
    #     print("cluster %s :" % label)
    #     for i in range(min(10, len(sentences))):  #随便打印几个，太多了看不过来
    #         print(sentences[i].replace(" ", ""))
    #     print("---------")

if __name__ == "__main__":
    main()

