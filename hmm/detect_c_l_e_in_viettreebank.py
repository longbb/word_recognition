# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import xml.etree.ElementTree as ET
from helper import Helper

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    viettreebank_path = module_path + '/data/viettreebank.xml'
    tree = ET.parse(viettreebank_path)
    root = tree.getroot()

    c_l_e_labels = set()

    labels = ['C', 'L', 'E', 'P', 'Nc', 'R']


    for label in labels:
        for c_label in root.findall('.//' + label):
            c_text = c_label.text.lower()
            if c_text not in c_l_e_labels and len(c_text.split()) == 1:
                c_l_e_labels.add(c_text)
                print c_text

    label = [u'còn', u'rất', u'cũng', u'đã']
    for p_label in label:
        if p_label not in c_l_e_labels:
            c_l_e_labels.add(p_label)

    result_data_path = module_path + '/data/c_e_l_viettreebank.pkl'
    Helper.save_obj(c_l_e_labels, result_data_path)
    print 'Save done!'

    result_data_path = module_path + '/data/c_e_l_viettreebank.txt'
    c_l_e_file = open(result_data_path, 'w')
    for word in c_l_e_labels:
        c_l_e_file.write(word.encode('utf8') + '\n')
    c_l_e_file.close()
    print 'Save done!'
