# coding: utf-8
import os.path, sys
import os
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
from model3 import Model_3
from model2 import Model_2
import multiprocessing
import numpy as np

if __name__ == '__main__':

    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'

    bigram_path = module_path + '/result_data/bigram.pkl'
    bigram_hash = Helper.load_obj(bigram_path)
    occurrences_data_path = module_path + '/result_data/occurrences.pkl'
    statistic_bigram = Helper.load_obj(occurrences_data_path)
    invert_bigram_path = module_path + '/result_data/invert_bigram.pkl'
    invert_bigram_hash = Helper.load_obj(invert_bigram_path)

    vlsp_folder_path = module_path + '/VLSP_Sentences'
    files = os.listdir(vlsp_folder_path)[:100]
    sentences = []
    for file in files:
        sentences.extend(Helper.read_vlsp_sentences(vlsp_folder_path + '/' + file))

    avg_precesion_array = []
    max_precesion = 0
    best_params = {}
    # for mbcon in np.arange(0.0001, 0.0041, 0.0001):
    #     for dcon in np.arange(0.0001, 0.0101, 0.0001):
    mbcon = 0.0005
    dcon = 0.0095
    word_array = set()
    lmc_more_2 = {}
    # probabilistic_model = ProbabilisticModel(mbcon, mbcon, 100, 100, dcon,
    #     bigram_hash, statistic_bigram, word_array, lmc_more_2)
    probabilistic_model = Model_3(mbcon, mbcon, 100, 100, dcon,
        bigram_hash, statistic_bigram, word_array, lmc_more_2, invert_bigram_hash)

    total_precesion = 0
    for sentence in sentences:
        not_split_sentences = sentence.replace("_", " ")
        precision = probabilistic_model.caculate_precesion(
            not_split_sentences, sentence)
        total_precesion += precision
    avg_precesion = total_precesion / len(sentences)
    print 'Precesion with mbcon is %f and dcon is %f: %f' % (mbcon, dcon, avg_precesion)
    avg_precesion_array.append({
        'avg_precesion': avg_precesion,
        'mbcon': mbcon,
        'dcon': dcon
    })
    if avg_precesion > max_precesion:
        max_precesion = avg_precesion
        best_params = {
            'mbcon': mbcon,
            'dcon': dcon
            }
    print 'Best params: mbcon is %f and dcon is %f and precesion is %f' % (
        best_params['mbcon'], best_params['dcon'], max_precesion)



