# -*- coding: utf-8 -*-
import re
import csv
import os
import xml.etree.ElementTree as ET
import pickle

class Helper(object):
    def __init__(self):
        pass

    @staticmethod
    def clear_str(string):
        char_special = '\,|\;|\(|\)|\>|\<|\'|\"'
        str_clean = re.sub('[' + char_special + ']', ' PUNC|SYSTEM_CODE ', string)
        str_clean = re.sub('[.]', ' ', str_clean)
        str_clean = str_clean.strip()
        return str_clean

    @staticmethod
    def merge_two_data(data1, data2):
        new_data = data2
        for key1, value1 in data1.iteritems():
            if key1 in new_data:
                for key2, value2 in value1.iteritems():
                    if key2 == 'number_occurrences':
                        continue

                    if key2 in new_data[key1]:
                        new_data[key1][key2]['array_article'].extend(
                            value2['array_article']
                        )
                        new_data[key1][key2]['number_occurrences'] += value2['number_occurrences']
                    else:
                        new_data[key1][key2] = value2
                new_data[key1]['number_occurrences'] += data1[key1]['number_occurrences']
            else:
                new_data[key1] = value1
        return new_data

    @staticmethod
    def read_file_csv(path):
        data = []
        with open(path, 'rb') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                data.append(row)
        csv_file.close()
        return data

    @staticmethod
    def load_syllables_dictionary(output_option='set'):
        module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
            '/word_recognition'
        path_to_dict = module_path + '/data/syllables_dictionary.txt'
        dict_file = open(path_to_dict, 'r')
        syllables_dictionary = []
        for line in dict_file:
            syllables_dictionary.append(line[:-1])

        if output_option == 'set':
            return set(syllables_dictionary)

        new_dict = {}
        for index, syllable in enumerate(syllables_dictionary):
            new_dict[syllable] = index
        return new_dict

    @staticmethod
    def load_wiki_data(path_to_file):
        xml_file = open(path_to_file, 'r')
        doc_array = []
        new_doc = ''
        for line in xml_file:
            if line[:4] == '<doc':
                new_doc = ''
            elif line[:5] == '</doc':
                doc_array.append(new_doc)
            else:
                new_doc += line
        # xml_file = '<root>\n'+ xml_file + '</root>'
        # parser = etree.XMLParser(recover=True)
        # # import pdb; pdb.set_trace()
        # root = ET.fromstring(xml_file, parser=parser)

        # doc_array = []
        # for doc in root.findall('doc'):
        #     doc_content = doc.text
        #     doc_array.append(doc_content)
        return doc_array

    @staticmethod
    def save_obj(obj, path_to_file):
        with open(path_to_file, 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_obj(path_to_file):
        with open(path_to_file, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def read_vlsp_sentences(path_to_file):
        xml_file = open(path_to_file, 'r')
        doc_array = []
        new_doc = ''
        for line in xml_file:
            if line[:6] == '<pBody':
                new_doc = ''
            elif line[:7] == '</pBody':
                doc_array.append(new_doc)
            else:
                new_doc += line
        return doc_array


    @staticmethod
    def read_dictionary(path_to_dict):
        dictionary = set()
        dict_file = open(path_to_dict, 'r')
        for line in dict_file:
            if '##' in line:
                index = line.rfind('#')
                word = line[index+1:-1]
                # import pdb; pdb.set_trace()
                word = word.replace(" ", "_")
                dictionary.add(word)
        return dictionary

    @staticmethod
    def read_new_dictionary(path_to_dict):
        dictionary = set()
        dict_file = open(path_to_dict, 'r')
        for line in dict_file:
            word = line.split('\t')[0]
            # import pdb; pdb.set_trace()
            dictionary.add(word)
        return dictionary
