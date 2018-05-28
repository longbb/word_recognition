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
import time
import multiprocessing

rule_01_done = 24360

class ProbabilisticModel(object):
    def __init__(self, mbcon, mtcon, mbsup, mtsup, dcon, bigram_hash, occurrences_statistic,
        word_array, lmc_more_2):
        self.sentence_database = Database('sentence_collection')
        self.bigram_database = Database('bigram_collection')
        self.word_database = Database('word_collection')
        self.mbcon = mbcon
        self.mtcon = mtcon
        self.mbsup = mbsup
        self.mtsup = mtsup
        self.dcon = dcon
        self.bigram_hash = bigram_hash
        self.occurrences_statistic = occurrences_statistic
        self.word_array = word_array
        self.lmc_more_2 = lmc_more_2

    def confident_model(self, first_syllable, second_syllable):
        bigram = first_syllable + ' ' + second_syllable
        bigram_probability = self.bigram_probability(bigram)['probability']
        first_syllable_probability = self.unigram_probability(
            first_syllable
        )['probability']
        second_syllable_probability = self.unigram_probability(
            second_syllable
        )['probability']
        if bigram_probability == 0:
            return 0
        confident = bigram_probability * bigram_probability
        confident = confident / (first_syllable_probability * second_syllable_probability)
        return confident

    def recognition_function(self, first_syllable, second_syllable):
        confident = self.confident_model(first_syllable, second_syllable)
        bigram = first_syllable + ' ' + second_syllable
        if self.check_name(first_syllable) and self.check_name(second_syllable):
            return 1
        if self.check_name(first_syllable) or self.check_name(second_syllable):
            return 0
        occurrences = self.__bigram_occurrences(bigram)
        if confident >= self.mtcon and occurrences >= self.mtsup:
            return 1
        if confident < self.mbcon and occurrences < self.mbsup:
            return -1
        return 0

    def detect_lmc(self, sentence):
        sentence = sentence[0].lower() + sentence[1:]
        word_array = sentence.split(' ')
        lmc_array = []
        for index, word in enumerate(word_array):
            if index == 0:
                new_lmc = [word_array[0]]
            else:
                first_syllable = word_array[index - 1]
                second_syllable = word
                recognition_value = self.recognition_function(first_syllable, second_syllable)
                if recognition_value == 1:
                    new_lmc.append(word)
                else:
                    lmc_array.append(new_lmc)
                    new_lmc = [word]
        lmc_array.append(new_lmc)
        return lmc_array

    def learning_process(self):
        number_article = self.sentence_database.collection.count()
        print 'Need learing %i article' % number_article
        index_article = 130
        for index in range(index_article, number_article):
            self.article_learning_01(index)

    def article_learning_01(self, index_article, article_content):
        print 'Start learning for article %s' % index_article
        article = Article(article_content, index_article, None)
        article.detect_paragraph()
        for paragraph in article.paragraphs:
            for sentence in paragraph:
                sentence = sentence.decode('utf-8').lower().encode('utf-8')
                self.rule_0_and_1(sentence)
        print 'Learning article %s done' % index_article

    def rule_0_and_1(self, sentence):
        # try:
        lmc_array = self.detect_lmc(sentence)

        for lmc_index, lmc in enumerate(lmc_array):
            link_lmc = self.__link_lmc(lmc)
            if link_lmc in self.word_array:
                lmc_array[lmc_index] = link_lmc
            elif len(lmc) == 2:
                lmc_array[lmc_index] = link_lmc
                # insert new word
                self.word_array.add(link_lmc)
            elif (len(lmc) == 1) and (link_lmc in self.bigram_hash):
                lmc_array[lmc_index] = link_lmc
                # insert new word
                self.word_array.add(link_lmc)
            elif len(lmc) > 2:
                if link_lmc in self.lmc_more_2:
                    self.lmc_more_2[link_lmc] += 1
                else:
                    self.lmc_more_2[link_lmc] = 1
        # except Exception as error:
        #     print 'Has an error %s' % str(error)

    def rule_2_and_3(self):
        print '%i lmc need handle' % len(self.lmc_more_2)
        number_done = 0
        for lmc, number_occurrences in self.lmc_more_2.iteritems():
            lmc_array = lmc.split('_')
            confident_array = []
            for word_index, word in enumerate(lmc_array):
                if word_index > 0:
                    confident_array.append(
                        self.confident_model(lmc_array[word_index - 1], word)
                    )
            max_confident_index = 0
            max_confident_value = 0
            second_confident_value = 0
            max_confident_position = 0
            for confident_index, confident in enumerate(confident_array):
                if confident > max_confident_value:
                    max_confident_position = confident_index
                    max_confident_index = confident_index
                    second_confident_value = max_confident_value
                    max_confident_value = confident
            different_confident = max_confident_value - second_confident_value
            if different_confident > self.dcon:
                new_word = self.__link_lmc([lmc[max_confident_index], lmc[max_confident_index + 1]])
                if new_word not in self.word_array:
                    self.word_array.add(new_word)
            else:
                if (number_occurrences > self.mtsup) and (lmc not in self.word_array) \
                    and (len(lmc_array) == 3):
                    self.word_array.add(lmc)
            number_done += 1
            print 'Lmc %i done' % number_done

    def word_recognition(self, sentence):
        lmc_array = self.detect_lmc(sentence)
        new_lmc_array = []

        for lmc_index, lmc in enumerate(lmc_array):
            link_lmc = self.__link_lmc(lmc)
            if link_lmc in self.word_array:
                new_lmc_array.append(link_lmc)
            elif len(lmc) <= 2:
                new_lmc_array.append(link_lmc)
            elif self.check_name(lmc[0]):
                new_lmc_array.append(link_lmc)
            else:
                confident_array = []
                for word_index, word in enumerate(lmc):
                    if word_index > 0:
                        confident_array.append(
                            self.confident_model(lmc[word_index - 1], word)
                        )
                max_confident_index = 0
                max_confident_value = 0
                second_confident_value = 0
                max_confident_position = 0
                for confident_index, confident in enumerate(confident_array):
                    if confident > max_confident_value:
                        max_confident_position = confident_index
                        max_confident_index = confident_index
                        second_confident_value = max_confident_value
                        max_confident_value = confident
                different_confident = max_confident_value - second_confident_value
                if different_confident > self.dcon:
                    new_lmc = []
                    word_index = 0
                    while word_index < len(lmc):
                        if word_index == len(lmc) - 1:
                            new_lmc.append(lmc[word_index])
                        else:
                            if word_index == max_confident_index:
                                new_lmc.append(
                                    self.__link_lmc([lmc[word_index], lmc[word_index + 1]])
                                )
                                word_index += 1
                            else:
                                new_lmc.append(lmc[word_index])
                        word_index += 1
                    new_lmc_array.append(' '.join(new_lmc))
                else:
                    new_lmc_array.append(' '.join(lmc))

        new_sentence = ' '.join(new_lmc_array)
        return new_sentence


    def unigram_probability(self, unigram):
        total_number_occurrences = self.occurrences_statistic['number_unigram_occurrences']
        if unigram not in self.bigram_hash:
            return {
                'probability': 0,
                'number_occurrences': 0,
                'total_number_occurrences': total_number_occurrences
            }
        unigram_occurrences = self.bigram_hash[unigram]['number_occurrences']
        probability = float(unigram_occurrences) / total_number_occurrences
        return {
            'probability': probability,
            'number_occurrences': unigram_occurrences,
            'total_number_occurrences': total_number_occurrences
        }

    def bigram_probability(self, bigram):
        total_number_occurrences = self.occurrences_statistic['number_bigram_occurrences']
        bigram_occurrences = self.__bigram_occurrences(bigram)
        probability = float(bigram_occurrences) / total_number_occurrences
        return {
            'probability': probability,
            'number_occurrences': bigram_occurrences,
            'total_number_occurrences': total_number_occurrences
        }

    def __bigram_occurrences(self, bigram):
        syllable_array = bigram.split(' ')
        first_syllable = syllable_array[0]
        if not first_syllable in self.bigram_hash:
            return 0
        first_syllable_info = self.bigram_hash[first_syllable]
        if bigram not in first_syllable_info:
            return 0
        return first_syllable_info[bigram]['number_occurrences']

    def __link_lmc(self, lmc):
        for word in lmc:
            return '_'.join(lmc)

    def __find_number_occurrences(self, lmc_string, array_article):
        number_occurrences = 0
        for article_index in array_article:
            find_article_data = self.sentence_database.find_one({
                'article_index': article_index
            })
            if not (find_article_data['success'] and find_article_data['object']):
                print 'Has an exception at %i' % article_index
                continue

            article_data = find_article_data['object']
            for sentence in article_data['data']:
                number_occurrences += sentence.count(lmc_string)
        return number_occurrences

    def caculate_precesion(self, source_sentence, destination_sentence):
        predict_sentence = self.word_recognition(source_sentence)
        predict_words = predict_sentence.split(' ')
        destination_words = destination_sentence.split(' ')
        number_correct_words = 0
        for predict_word in predict_words:
            if predict_word in destination_words:
                number_correct_words += 1
        return {
            'precision': float(number_correct_words) / len(predict_words),
            'number_predict': len(predict_words),
            'number_predict_true': number_correct_words,
            'number_destination_word': len(destination_words)
        }

    def evaluate(self, path_to_evaluate_data):
        evaluate_data = Helper.read_file_csv(path_to_evaluate_data)
        max_precesion = 0
        min_precesion = 1
        total_precesion = 0
        array_precesion = []
        for index, data in enumerate(evaluate_data):
            print 'Predict for sentence %i' % index
            precision = self.caculate_precesion(data[0].decode('utf-8'), data[1].decode('utf-8'))['precision']
            if precision > max_precesion:
                max_precesion = precision
            if precision < min_precesion:
                min_precesion = precision
            total_precesion += precision
            array_precesion.append(precision)
        average_precesion = total_precesion / len(evaluate_data)
        print 'Max precesion: %f' % max_precesion
        print 'Min precesion: %f' % min_precesion
        print 'Average precesion: %f' % average_precesion
        import pdb; pdb.set_trace()
        return {
            'max_precesion': max_precesion,
            'min_precesion': min_precesion,
            'average_precesion': average_precesion,
            'array_precesion': array_precesion
        }

    def check_name(self, syllable):
        if not syllable:
            return False
        if syllable[0].isupper():
            return True
        return False

if __name__ == '__main__':
    mbcon = 0.0005
    mtcon = 0.0005
    mbsup = 100
    mtsup = 100
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'
    bigram_path = module_path + '/result_data/bigram.pkl'
    bigram_hash = Helper.load_obj(bigram_path)
    occurrences_data_path = module_path + '/result_data/occurrences.pkl'
    statistic_bigram = Helper.load_obj(occurrences_data_path)
    word_array = set()
    lmc_more_2 = {}

    probabilistic_model = ProbabilisticModel(mbcon, mtcon, mbsup, mtsup, 1,
        bigram_hash, statistic_bigram, word_array, lmc_more_2)
    sentence = Helper.clear_str('Ấm lên toàn cầu, nóng lên toàn cầu, hay hâm nóng toàn cầu là hiện tượng nhiệt độ trung bình của không khí và các đại dương trên Trái Đất tăng lên theo các quan sát trong các thập kỷ gần đây').decode('utf-8')
    lmc_array = probabilistic_model.word_recognition(sentence)
    print lmc_array
