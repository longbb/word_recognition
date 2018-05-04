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

    # unsupervised
    # hmm_save_path = module_path + '/hmm/hmm_data/hmm_model.dill'
    # supervised
    hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmm_model.dill'
    hmm_tagger = HiddenMarkovModel()
    hmm_tagger.load_model(hmm_save_path)

    vlsp_folder_path = module_path + '/VLSP_Sentences/test'
    files = os.listdir(vlsp_folder_path)
    test_sentences = []
    for file in files:
        test_sentences.extend(Helper.read_vlsp_sentences(vlsp_folder_path + '/' + file))

    vlsp_folder_path = module_path + '/VLSP_Sentences/train'
    files = os.listdir(vlsp_folder_path)
    train_sentences = []
    for file in files:
        train_sentences.extend(Helper.read_vlsp_sentences(vlsp_folder_path + '/' + file))

    total_precision = 0
    max_precision = 0
    min_precision = 100
    number_predict = 0
    for index_sentence, sentence in enumerate(test_sentences):
        not_split_sentences = sentence.replace("_", " ")
        unlabeled_sequence = not_split_sentences.split()
        labeled_sequence = []
        for word in sentence.split():
            syllable_array = word.split('_')
            for index, syllable in enumerate(syllable_array):
                label = 0 if index == 0 else 1
                labeled_sequence.append(label)
        precision = hmm_tagger.caculate_precesion(unlabeled_sequence, labeled_sequence)
        if not (unlabeled_sequence and labeled_sequence):
            continue
        if not precision['success']:
            print 'Has an exception: %s' % str(precision['message'])
            continue
        precision = precision['object']
        total_precision += precision
        if precision > max_precision:
            max_precision = precision
        if precision < min_precision:
            min_precision = precision
        number_predict += 1
        print 'Precesion for sentence %i: %f' % (index_sentence, precision)

    avg_precision = total_precision / number_predict

    print 'Average precision: %f' % avg_precision
    print 'Max precision: %f' % max_precision
    print 'Min precision: %f' % min_precision
