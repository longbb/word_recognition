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
from model2 import Model_2
import multiprocessing

def article_learning(index_article):
    mbcon = 0.03
    mtcon = 0.03
    mbsup = 100
    mtsup = 100
    probabilistic_model = ProbabilisticModel(mbcon, mtcon, mbsup, mtsup, 1)
    probabilistic_model.article_learning_01(index_article)

if __name__ == '__main__':
    # rule 0 and 1
    array_data_file = {
        'AA': 100,
        'AB': 100,
        'AC': 100,
        'AD': 100,
        'AE': 100,
        'AF': 100,
        'AG': 100,
        'AH': 82
    }
    mbcon = 0.0015
    mtcon = 0.0015
    mbsup = 50
    mtsup = 50
    c = 0.0077

    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'
    bigram_path = module_path + '/result_data/bigram.pkl'
    bigram_hash = Helper.load_obj(bigram_path)
    occurrences_data_path = module_path + '/result_data/occurrences.pkl'
    statistic_bigram = Helper.load_obj(occurrences_data_path)
    word_array = set()
    lmc_more_2 = {}


    for folder, max_file in array_data_file.iteritems():
        print '=======================***%s***=======================' % folder
        for index_file in range(0, max_file):
            if index_file < 10:
                file_name = '0' + str(index_file)
            else:
                file_name = str(index_file)
            print 'Start handle data in file %s in folder %s' % (file_name, folder)

            wiki_data_path = '/viwiki_data/' + folder + '/wiki_' + file_name
            wiki_data_path = module_path + wiki_data_path
            doc_array = Helper.load_wiki_data(wiki_data_path)

            position_file = '%s_%s' % (folder, file_name)

            for index, doc in enumerate(doc_array):
                position_file = '%i_%s_%s' % (index, file_name, folder)
                probabilistic_model = ProbabilisticModel(mbcon, mtcon, mbsup, mtsup, 0.0077,
                    bigram_hash, statistic_bigram, word_array, lmc_more_2)
                probabilistic_model.article_learning_01(position_file, doc)
                word_array = probabilistic_model.word_array
                lmc_more_2 = probabilistic_model.lmc_more_2

    print 'Has %i word detect' % len(word_array)
    print 'Has %i lmc need handle' % len(lmc_more_2)

    two_syllables_path = module_path + '/result_data/two_syllables_word.pkl'
    Helper.save_obj(word_array, two_syllables_path)

    lmc_more_2_path = module_path + '/result_data/lmc_more_2.pkl'
    Helper.save_obj(lmc_more_2, lmc_more_2_path)

    two_syllables_path = module_path + '/result_data/two_syllables_word.pkl'
    word_array = Helper.load_obj(two_syllables_path)

    lmc_more_2_path = module_path + '/result_data/lmc_more_2.pkl'
    lmc_more_2 = Helper.load_obj(lmc_more_2_path)

    probabilistic_model = ProbabilisticModel(mbcon, mtcon, mbsup, mtsup, 0.0077,
        bigram_hash, statistic_bigram, word_array, lmc_more_2)
    probabilistic_model.rule_2_and_3()
    word_array = probabilistic_model.word_array
    lmc_more_2 = probabilistic_model.lmc_more_2

    print 'Has %i word detect' % len(word_array)

    two_syllables_path = module_path + '/result_data/two_syllables_word.pkl'
    Helper.save_obj(word_array, two_syllables_path)
