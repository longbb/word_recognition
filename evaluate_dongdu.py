# coding: utf-8
import os
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'

    vlsp_folder_path = module_path + '/VLSP_Sentences/test_100_articles'
    dongdu_test_file = module_path + '/test_dongdu'
    dongdu_file = module_path + '/dongdu'
    files = os.listdir(vlsp_folder_path)
    test_sentences = []
    number_predict_true = 0
    total_predict = 0
    number_destination_predict = 0

    input_path = dongdu_file + "/test_input.txt"
    output_path = dongdu_file + "/test_output.txt"
    wrong_word = []
    for file in files:
        print 'Handle file %s' % file
        vlsp_sentences = Helper.read_vlsp_sentences(vlsp_folder_path + '/' + file)
        for vlsp_sentence in vlsp_sentences:
            vlsp_words = vlsp_sentence.split()
            if not vlsp_words:
                continue
            input_file = open(input_path, "w")
            input_file.write(vlsp_sentence)
            input_file.close()

            segment_command = dongdu_file + "/predictor -i " + input_path + " -o " + output_path
            os.system(segment_command)
            output_file = open(output_path, "r")
            dongdu_sentence = output_file.read()
            output_file.close()
            dongdu_words = dongdu_sentence.split()
            total_predict += len(dongdu_words)
            number_destination_predict += len(vlsp_words)
            for index, dongdu_word in enumerate(dongdu_words):
                if dongdu_word in vlsp_words:
                    number_predict_true += 1
                elif not dongdu_word:
                    number_predict_true += 1
                elif not dongdu_word[0].isalpha():
                    number_predict_true += 1
                else:
                    wrong_word.append(dongdu_word)

    print '======================Wrong word======================'
    for word in wrong_word:
        print word

    precision = float(number_predict_true) / total_predict
    recall = float(number_predict_true) / number_destination_predict
    print 'Precesion: %f' % precision
    print 'Recall: %f' % recall
