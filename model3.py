# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
from probabilistic_model import ProbabilisticModel
import csv
import pymongo
from pymongo import MongoClient
import math
import threading
import time

class Model_3(ProbabilisticModel):
    def __init__(self, mbcon, mtcon, mbsup, mtsup, dcon, bigram_hash, occurrences_statistic,
        word_array, lmc_more_2, invert_bigram_hash):
        super(self.__class__, self).__init__(mbcon, mtcon, mbsup, mtsup, dcon,
            bigram_hash, occurrences_statistic, word_array, lmc_more_2)
        self.invert_bigram_hash = invert_bigram_hash

    def confident_model(self, first_syllable, second_syllable):
        bigram = first_syllable + ' ' + second_syllable

        if first_syllable not in self.bigram_hash:
            return 0
        if second_syllable not in self.invert_bigram_hash:
            return 0

        first_syllable_hash = self.bigram_hash[first_syllable]
        total_bigram_occurrences = first_syllable_hash['number_occurrences_in_bigram']
        if bigram in first_syllable_hash:
            bigram_occurrences = first_syllable_hash[bigram]['number_occurrences']
        else:
            return 0

        first_probabilistic = float(bigram_occurrences) / total_bigram_occurrences

        second_syllable_hash = self.invert_bigram_hash[second_syllable]
        total_invert_bigram_occurrences = second_syllable_hash['number_occurrences_in_bigram']
        if bigram in second_syllable_hash:
            invert_bigram_occurrences = second_syllable_hash[bigram]['number_occurrences']
        else:
            return 0

        second_probabilistic = float(invert_bigram_occurrences) / total_invert_bigram_occurrences

        return first_probabilistic * second_probabilistic

if __name__ == '__main__':
    mbcon = 0.0015
    mtcon = 0.0015
    mbsup = 100
    mtsup = 100
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'
    bigram_path = module_path + '/result_data/bigram.pkl'
    bigram_hash = Helper.load_obj(bigram_path)
    occurrences_data_path = module_path + '/result_data/occurrences.pkl'
    statistic_bigram = Helper.load_obj(occurrences_data_path)
    invert_bigram_path = module_path + '/result_data/invert_bigram.pkl'
    invert_bigram_hash = Helper.load_obj(invert_bigram_path)
    word_array = set()
    lmc_more_2 = {}
    print 'Load data done!'
    probabilistic_model = Model_3(mbcon, mtcon, mbsup, mtsup, 0.0077, bigram_hash, statistic_bigram, word_array, lmc_more_2, invert_bigram_hash)
    sentence = Helper.clear_str('Ấm lên toàn cầu, nóng lên toàn cầu, hay hâm nóng toàn cầu là hiện tượng nhiệt độ trung bình của không khí và các đại dương trên Trái Đất tăng lên theo các quan sát trong các thập kỷ gần đây').decode('utf-8').lower().encode('utf-8')
    lmc_array = probabilistic_model.detect_lmc(sentence)

    confident_model = probabilistic_model.confident_model('đại', 'dương')
    import pdb; pdb.set_trace()
