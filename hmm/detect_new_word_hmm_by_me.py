# coding: utf-8
import os
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from database import Database
from article import Article
from helper import Helper
from hmm_written_by_me import HiddenMarkovModel
import random

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hmm_by_me_dictionary_path = module_path + '/hmm/hmm_data/hmm_by_me_dictionary_without_cle_all_new_dict.pkl'
    hmm_dictionary = Helper.load_obj(hmm_by_me_dictionary_path)

    invert_dictionary_path = module_path + '/hmm/hmm_data/invert_hmm_by_me_dictionary_without_cle_all_new_dict.pkl'
    invert_hmm_dictionary = Helper.load_obj(invert_dictionary_path)

    hmm_save_path = module_path + '/hmm/hmm_data/unsupervised_hmm_by_me_without_cle_all_new_dict.pkl'
    hmm = Helper.load_obj(hmm_save_path)

    vlsp_word_path = module_path + '/data/bkdictionary.txt'
    vlsp_word_array = Helper.read_new_dictionary(vlsp_word_path)

    occurrences_data_path = module_path + '/hmm/hmm_data/occurrences.pkl'
    statistic_bigram = Helper.load_obj(occurrences_data_path)

    #test with sub parameter
    bigram_path = module_path + '/hmm/hmm_data/bigram.pkl'
    bigram_hash = Helper.load_obj(bigram_path)
    invert_bigram_path = module_path + '/hmm/hmm_data/invert_bigram.pkl'
    invert_bigram_hash = Helper.load_obj(invert_bigram_path)

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

    hmm_new_word = {}
    number_doc = 0
    number_sentence = 0
    sentence_choose = []

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
                print 'Start training in doc %i of file %s' % (index, folder)
                number_doc += 1
                article = Article(doc, position_file, hmm_dictionary)
                article.detect_paragraph()
                for paragraph in article.paragraphs:
                    for sentence in paragraph:
                        number_sentence += 1
                        sentence = sentence.lower()
                        array_syllables = sentence.split()

                        sentence_object = Article(sentence, position_file, hmm_dictionary)
                        article_unlabeled_sequences = sentence_object.convert_syllable_to_number()
                        state_sequence = hmm.veterbi_algorithm(
                            article_unlabeled_sequences[0],
                            using_sub_params=True,
                            bigram_hash=bigram_hash,
                            invert_bigram_hash=invert_bigram_hash,
                            number_occurrences=statistic_bigram,
                            invert_dictionary=invert_hmm_dictionary
                        )

                        try:
                            word_array = []
                            syllables = sentence.split()
                            index_state = 0
                            new_word = []
                            for syllable in syllables:
                                if index_state >= len(state_sequence):
                                    break
                                if syllable in article.syllables_dictionary:
                                    if state_sequence[index_state] == 1:
                                        new_word.append(syllable)
                                    else:
                                        if new_word:
                                            word_array.append('_'.join(new_word))
                                        new_word = [syllable]
                                    index_state += 1
                                else:
                                    if new_word:
                                        word_array.append('_'.join(new_word))
                                    new_word = [syllable]
                                    if state_sequence[index_state] == 2 and index_state < len(state_sequence) - 1:
                                        index_state += 1
                            word_array.append('_'.join(new_word))

                            if len(sentence_choose) < 100 and len(array_syllables) >= 7:
                                rand = random.random()
                                if rand < 0.5:
                                    sentence_choose.append({
                                        'source': sentence.decode('utf-8'),
                                        'predict': ' '.join(word_array).decode('utf-8')
                                    })

                        except Exception as error:
                            continue

                        for word in word_array:
                            if word in vlsp_word_array:
                                continue
                            if word in hmm_new_word:
                                hmm_new_word[word] += 1
                                continue
                            syllables = word.split('_')
                            check_vietnamese = True
                            for syllable in syllables:
                                if syllable not in article.syllables_dictionary:
                                    check_vietnamese = False
                                    break
                            if not check_vietnamese:
                                continue
                            hmm_new_word[word] = 1

    set_new_word = []
    for word, number_occurrences in hmm_new_word.iteritems():
        if number_occurrences > 50:
            set_new_word.append(word)

    new_word_text_file = module_path + '/result_data/hmm_by_me_new_word_all_combined.txt'
    file = open(new_word_text_file, 'w')

    for word in set_new_word:
        file.write(word.decode('utf8').encode('utf8') + '\n')
    file.close()

    sentence_test = module_path + '/result_data/hmm_by_me_test_sentence_all_combined.txt'
    sentence_file = open(sentence_test, 'w')

    for senetence in sentence_choose:
        sentence_file.write(senetence['predict'].encode('utf8') + '\n')
    sentence_file.close()
