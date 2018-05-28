# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
from hmm import HiddenMarkovModel
import csv
import nltk
import dill

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    syllables_dictionary = Helper.load_syllables_dictionary()
    article = Article('', 0, syllables_dictionary)

    #load model
    hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmm_model.dill'
    hmm_tagger = HiddenMarkovModel()
    hmm_tagger.load_model(hmm_save_path)

    vlsp_folder_path = module_path + '/VLSP_Sentences/test'
    files = os.listdir(vlsp_folder_path)
    test_sentences = []
    for file in files:
        posts = Helper.read_vlsp_sentences(vlsp_folder_path + '/' + file)
        for post in posts:
            article = Article(post, 0, syllables_dictionary)
            article.detect_paragraph()
            for paragraph in article.paragraphs:
                for sentence in paragraph:
                    test_sentences.append(sentence)

    total_precision = 0
    max_precision = 0
    min_precision = 100
    number_predict_true = 0
    number_predict = 0
    number_destination_word = 0
    for index_sentence, sentence in enumerate(test_sentences):
        not_split_sentences = sentence.replace("_", " ")
        unlabeled_sequence = not_split_sentences.split()
        eval_precision = hmm_tagger.caculate_precesion(unlabeled_sequence, sentence.split())
        if not eval_precision['success']:
            print 'Has an exception: %s' % str(eval_precision['message'])
            continue
        precision = eval_precision['object']
        number_predict_true += eval_precision['number_predict_true']
        number_predict += eval_precision['number_predict']
        number_destination_word += eval_precision['number_destination_word']
        total_precision += precision
        if precision > max_precision:
            max_precision = precision
        if precision < min_precision:
            min_precision = precision
        print 'Precesion for sentence %i: %f' % (index_sentence, precision)

    avg_precision = total_precision / len(test_sentences)

    print 'Average precision: %f' % avg_precision
    print 'Max precision: %f' % max_precision
    print 'Min precision: %f' % min_precision
    print 'Precision in words: %f' % (float(number_predict_true) / number_predict)
    print 'Recall: %f' % (float(number_predict_true) / number_destination_word)
