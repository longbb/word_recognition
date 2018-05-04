# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
from hmm_written_by_me import HiddenMarkovModel
import csv
import nltk
import dill

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    syllables_dictionary = Helper.load_syllables_dictionary()
    article = Article('', 0, syllables_dictionary)

    hmm_by_me_dictionary_path = module_path + '/hmm/hmm_data/hmm_by_me_dictionary_without_cle_all.pkl'
    hmm_dictionary = Helper.load_obj(hmm_by_me_dictionary_path)

    hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmm_by_me_without_cle_all.pkl'
    hmm = Helper.load_obj(hmm_save_path)

    vlsp_folder_path = module_path + '/VLSP_Sentences/test'
    files = os.listdir(vlsp_folder_path)
    test_sentences = []
    for file in files:
        test_sentences.extend(Helper.read_vlsp_sentences(vlsp_folder_path + '/' + file))

    total_precision = 0
    max_precision = 0
    min_precision = 100
    number_predict = 0
    number_word_predict_true = 0
    total_word_predict = 0
    for index_sentence, sentence in enumerate(test_sentences):
        sentence = sentence.lower()
        not_split_sentences = sentence.replace("_", " ")
        unlabeled_sequence = not_split_sentences.split()
        sentence_object = Article(' '.join(unlabeled_sequence), index_sentence, hmm_dictionary)
        article_unlabeled_sequences = sentence_object.convert_syllable_to_number()
        if not article_unlabeled_sequences:
            continue
        state_sequence = hmm.veterbi_algorithm(article_unlabeled_sequences[0])

        labeled_sequence = []
        for word in sentence.split():
            syllable_array = word.split('_')
            for index, syllable in enumerate(syllable_array):
                if syllable not in hmm_dictionary:
                    label = 2
                    if (not labeled_sequence) or (labeled_sequence[-1] != 2):
                        labeled_sequence.append(label)
                else:
                    label = 0 if index == 0 else 1
                    labeled_sequence.append(label)

        total_syllable = len(state_sequence)
        if not total_syllable:
            continue

        if not (state_sequence and labeled_sequence):
            continue

        number_predict_true = 0
        for index_state, state in enumerate(state_sequence):
            try:
                total_word_predict += 1
                if state == labeled_sequence[index_state]:
                    number_predict_true += 1
                    number_word_predict_true += 1
            except Exception as error:
                import pdb; pdb.set_trace()

        precision = float(number_predict_true) / total_syllable
        total_precision += precision
        if precision > max_precision:
            max_precision = precision
        if precision < min_precision:
            min_precision = precision
        number_predict += 1
        print 'Precesion for sentence %i: %f' % (index_sentence, precision)

    avg_precision = total_precision / number_predict
    avg_precision_in_word = float(number_word_predict_true) / total_word_predict

    print 'Average precision: %f' % avg_precision
    print 'Average precision in word: %f' % avg_precision_in_word
    print 'Max precision: %f' % max_precision
    print 'Min precision: %f' % min_precision
