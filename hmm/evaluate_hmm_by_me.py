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

    hmm_by_me_dictionary_path = module_path + '/hmm/hmm_data/hmm_by_me_dictionary_without_cle_all_new_dict.pkl'
    hmm_dictionary = Helper.load_obj(hmm_by_me_dictionary_path)

    invert_dictionary_path = module_path + '/hmm/hmm_data/invert_hmm_by_me_dictionary_without_cle_all_new_dict.pkl'
    invert_hmm_dictionary = Helper.load_obj(invert_dictionary_path)

    hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmm_by_me_without_cle_all_new_dict.pkl'
    hmm = Helper.load_obj(hmm_save_path)

    occurrences_data_path = module_path + '/hmm/hmm_data/occurrences.pkl'
    statistic_bigram = Helper.load_obj(occurrences_data_path)

    #test with sub parameter
    bigram_path = module_path + '/hmm/hmm_data/bigram.pkl'
    bigram_hash = Helper.load_obj(bigram_path)
    invert_bigram_path = module_path + '/hmm/hmm_data/invert_bigram.pkl'
    invert_bigram_hash = Helper.load_obj(invert_bigram_path)

    vlsp_folder_path = module_path + '/VLSP_Sentences/test'
    files = os.listdir(vlsp_folder_path)
    test_sentences = []
    for file in files:
        posts = Helper.read_vlsp_sentences(vlsp_folder_path + '/' + file)
        for post in posts:
            article = Article(post, 0, hmm_dictionary)
            article.detect_paragraph()
            for paragraph in article.paragraphs:
                for sentence in paragraph:
                    test_sentences.append(sentence)

    total_precision = 0
    max_precision = 0
    min_precision = 100
    number_predict = 0
    number_word_predict_true = 0
    total_word_predict = 0
    total_word_must_predict = 0
    predict_fail = []

    for index_sentence, sentence in enumerate(test_sentences):
        if not sentence:
            continue
        sentence = sentence[0].lower() + sentence[1:]
        not_split_sentences = sentence.replace("_", " ")
        unlabeled_sequence = not_split_sentences.split()
        sentence_object = Article(' '.join(unlabeled_sequence), index_sentence, hmm_dictionary)
        article_unlabeled_sequences = sentence_object.convert_syllable_to_number()
        if not article_unlabeled_sequences or len(article_unlabeled_sequences[0]) <= 5:
            continue
        state_sequence = hmm.veterbi_algorithm(
            article_unlabeled_sequences[0],
            using_sub_params=True,
            bigram_hash=bigram_hash,
            invert_bigram_hash=invert_bigram_hash,
            number_occurrences=statistic_bigram,
            invert_dictionary=invert_hmm_dictionary
        )

        labeled_sequence = []
        for word in sentence.split():
            syllable_array = word.split('_')
            for index, syllable in enumerate(syllable_array):
                if syllable not in hmm_dictionary:
                    label = 2
                    if (not labeled_sequence) or (labeled_sequence[-1] != 2):
                        labeled_sequence.append(label)
                else:
                    if index == 0 or labeled_sequence[-1] == 2:
                        label = 0
                    else:
                        label = 1
                    labeled_sequence.append(label)

        total_syllable = len(state_sequence)
        if not total_syllable:
            continue

        if not (state_sequence and labeled_sequence):
            continue

        labeled_words = []
        predict_words = []
        label_detected_word = []
        predict_detected_word = []

        check_valid = True
        for index, syllable in enumerate(article_unlabeled_sequences[0]):
            try:
                syllable = str(syllable)
                if labeled_sequence[index] == 0 or labeled_sequence[index] == 2:
                    if label_detected_word:
                        labeled_words.append('_'.join(label_detected_word))
                    label_detected_word = [syllable]
                else:
                    label_detected_word.append(syllable)

                if state_sequence[index] == 0 or state_sequence[index] == 2:
                    if predict_detected_word:
                        predict_words.append('_'.join(predict_detected_word))
                    predict_detected_word = [syllable]
                else:
                    predict_detected_word.append(syllable)
            except Exception as error:
                check_valid = False
                break
        labeled_words.append('_'.join(label_detected_word))
        predict_words.append('_'.join(predict_detected_word))

        if not check_valid:
            continue

        number_predict_true = 0
        total_word_must_predict += len(labeled_words)
        for predict_word in predict_words:
            total_word_predict += 1
            if predict_word in labeled_words:
                number_predict_true += 1
                number_word_predict_true += 1
            else:
                predict_fail.append(predict_word)
        if not predict_words:
            continue
        precision = float(number_predict_true) / len(predict_words)

        total_precision += precision
        if precision > max_precision:
            max_precision = precision
        if precision < min_precision:
            min_precision = precision
        number_predict += 1
        print 'Precesion for sentence %i: %f' % (index_sentence, precision)

    avg_precision = total_precision / number_predict
    avg_precision_in_word = float(number_word_predict_true) / total_word_predict
    recall = float(number_word_predict_true) / total_word_must_predict

    print 'Average precision: %f' % avg_precision
    print 'Average precision in word: %f' % avg_precision_in_word
    print 'Recall: %f' % recall
    print 'Max precision: %f' % max_precision
    print 'Min precision: %f' % min_precision
