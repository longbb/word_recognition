# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
import csv
import pymongo
from pymongo import MongoClient
import math
import threading
from probabilistic_model import ProbabilisticModel
import multiprocessing

def article_learning(index_article):
    mbcon = 0.03
    mtcon = 0.03
    mbsup = 100
    mtsup = 100
    probabilistic_model = ProbabilisticModel(mbcon, mtcon, mbsup, mtsup, 1)
    probabilistic_model.article_learning_01(index_article)

if __name__ == '__main__':
    sentence_database = Database('sentence_collection')
    number_article = sentence_database.collection.count()
    print 'Need learing %i article' % number_article
    index_article = 24360
    while index_article < number_article:
        processes = []
        for index in range(index_article, index_article + 10):
            processes.append(
                multiprocessing.Process(target=article_learning, args=(
                    index,
                ))
            )
            processes[-1].start()
        for process in processes:
            process.join()
        print 'Learning article %i - %i done' % (index_article, index_article + 10)
        index_article += 10
