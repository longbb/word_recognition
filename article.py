# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import re
from helper import Helper
from database import Database
import threading

class Article(object):
    def __init__(self, content, index_article, syllables_dictionary):
        self.content = content
        self.index_article = index_article
        self.syllables_dictionary = syllables_dictionary
        self.paragraphs = []

    def detect_paragraph(self):
        self.paragraphs = self.content.split('\n')
        self.paragraphs = self.split_sentences(self.paragraphs)

    def split_sentences(self, paragraphs_array):
        array_pharagraph_with_sentence = []
        for paragraph in paragraphs_array:
            if paragraph:
                paragraph = re.sub("\s\s+" , ". ", paragraph)
                regex = '\.+\s+|\:\s*|\!\s*|\?\s*'
                senetence_in_pharagraph = re.split(regex, paragraph)
                sentences = []
                for sentence in senetence_in_pharagraph:
                    if sentence:
                        new_sentence = Helper.clear_str(sentence)
                        # new_sentence = new_sentence.replace('\xc2\xa0\xc2\xa0', '')
                        if new_sentence:
                            sentences.append(new_sentence)
                array_pharagraph_with_sentence.append(sentences)
        return array_pharagraph_with_sentence

    def get_bigram(self):
        if not self.paragraphs:
            self.detect_paragraph()

        bigram_hash = {}
        for paragraph in self.paragraphs:
            for sentence in paragraph:
                words_array = sentence.split(' ')
                for index, word in enumerate(words_array):
                    word_type = self.check_type_syllable(word)
                    if word_type == 'VIETNAMESE_SYLLABLE|SYSTEM_CODE':
                        if index == (len(words_array) - 1):
                            if word in bigram_hash:
                                bigram_hash[word]['number_occurrences'] += 1
                            else:
                                bigram_hash[word] = {
                                    'number_occurrences': 1
                                }
                        else:
                            next_word = words_array[index + 1]
                            next_word_type = self.check_type_syllable(next_word)
                            if next_word_type == 'VIETNAMESE_SYLLABLE|SYSTEM_CODE':
                                bigram = word + ' ' + next_word

                                if word in bigram_hash:
                                    if bigram in bigram_hash[word]:
                                        bigram_hash[word][bigram]['number_occurrences'] += 1
                                    else:
                                        bigram_hash[word][bigram] = {
                                            'array_article': [self.index_article],
                                            'number_occurrences': 1
                                        }
                                    bigram_hash[word]['number_occurrences'] += 1
                                else:
                                    bigram_hash[word] = {
                                        bigram: {
                                            'array_article': [self.index_article],
                                            'number_occurrences': 1
                                        },
                                        'number_occurrences': 1
                                }
                            else:
                                if word in bigram_hash:
                                    bigram_hash[word]['number_occurrences'] += 1
                                else:
                                    bigram_hash[word] = {
                                        'number_occurrences': 1
                                    }
        return bigram_hash

    def invert_bigram(self):
        if not self.paragraphs:
            self.detect_paragraph()

        bigram_hash = {}
        for paragraph in self.paragraphs:
            for sentence in paragraph:
                words_array = sentence.split(' ')
                for index, word in enumerate(words_array):
                    word_type = self.check_type_syllable(word)
                    if word_type == 'VIETNAMESE_SYLLABLE|SYSTEM_CODE':
                        if index == 0:
                            if word in bigram_hash:
                                bigram_hash[word]['number_occurrences'] += 1
                            else:
                                bigram_hash[word] = {
                                    'number_occurrences': 1
                                }
                        else:
                            previous_word = words_array[index - 1]
                            previous_word_type = self.check_type_syllable(previous_word)
                            if previous_word_type == 'VIETNAMESE_SYLLABLE|SYSTEM_CODE':
                                bigram = previous_word + ' ' + word

                                if word in bigram_hash:
                                    if bigram in bigram_hash[word]:
                                        bigram_hash[word][bigram]['number_occurrences'] += 1
                                    else:
                                        bigram_hash[word][bigram] = {
                                            'array_article': [self.index_article],
                                            'number_occurrences': 1
                                        }
                                    bigram_hash[word]['number_occurrences'] += 1
                                else:
                                    bigram_hash[word] = {
                                        bigram: {
                                            'array_article': [self.index_article],
                                            'number_occurrences': 1
                                        },
                                        'number_occurrences': 1
                                }
                            else:
                                if word in bigram_hash:
                                    bigram_hash[word]['number_occurrences'] += 1
                                else:
                                    bigram_hash[word] = {
                                        'number_occurrences': 1
                                    }
        return bigram_hash

    def check_type_syllable(self, syllable):
        if syllable in self.syllables_dictionary:
            return 'VIETNAMESE_SYLLABLE|SYSTEM_CODE'
        if syllable.isalpha():
            return 'FOREIGN_SYLLABLE|SYSTEM_CODE'
        if syllable.isdigit():
            return 'DIGIT|SYSTEM_CODE'
        return 'CODE|SYSTEM_CODE'

    def get_hmm_training(self):
        """
        Usage: This function will prepare training data for HMM
        """
        if not self.paragraphs:
            self.detect_paragraph()

        training_data = []
        for paragraph in self.paragraphs:
            for sentence in paragraph:
                sentence = sentence[0].lower() + sentence[1:]
                sentence_training_data = []
                syllables = sentence.split()
                for syllable in syllables:
                    syllable_type = self.check_type_syllable(syllable)
                    if syllable_type == 'VIETNAMESE_SYLLABLE|SYSTEM_CODE':
                        sentence_training_data.append((syllable, ''))
                    else:
                        sentence_training_data.append((syllable_type, ''))
                training_data.append(sentence_training_data)
        return training_data

    def convert_syllable_to_number(self):
        """
        Usage: This funtion will convert syllable in article to number
        Require: The syllables_dictionary must be dict, not set
        """
        if not self.paragraphs:
            self.detect_paragraph()

        new_article = []
        not_vietnamese_code = self.syllables_dictionary['NOT_VIETNAMESE']
        for paragraph in self.paragraphs:
            for sentence in paragraph:
                sentence = sentence[0].lower() + sentence[1:]
                sentence_training_data = []
                syllables = sentence.split()
                for syllable in syllables:
                    if syllable in self.syllables_dictionary:
                        syllable_number = self.syllables_dictionary[syllable]
                        sentence_training_data.append(syllable_number)
                    else:
                        syllable_number = not_vietnamese_code
                        if not sentence_training_data:
                            sentence_training_data.append(syllable_number)
                        elif sentence_training_data[-1] != not_vietnamese_code:
                            sentence_training_data.append(syllable_number)
                new_article.append(sentence_training_data)
        return new_article


if __name__ == '__main__':
    # syllables_dictionary = Helper.load_syllables_dictionary()
    # content = 'Đây là nội dung thử nghiệm. Hôm qua trời nắng nhưng hôm nay trời rất âm u'.lower()
    # article = Article(content, 1, syllables_dictionary)
    # content2 = 'Hôm nay U23 Việt Nam thắng, vui quá'.lower()
    # article2 = Article(content2, 2, syllables_dictionary)
    # bigram_hash2 = article2.get_bigram()
    # bigram_hash = article.get_bigram()
    # new_hash = Helper.merge_two_data(bigram_hash, bigram_hash2)
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
        '/word_recognition'
    wiki_data_path = module_path + '/viwiki_data/AA/wiki_00'
    doc_array = Helper.load_wiki_data(wiki_data_path)
    import pdb; pdb.set_trace()
