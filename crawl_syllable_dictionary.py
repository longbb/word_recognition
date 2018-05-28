# coding: utf-8
import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from bs4 import BeautifulSoup
import urllib2

class SyllableDictionaryCrawler(object):
    def __init__(self):
        self.crawled_page = 'http://www.vietnamtudien.org/vntd-kttd/'

    def crawl(self):
        html_doc = urllib2.urlopen(self.crawled_page).read()
        soup = BeautifulSoup(html_doc, 'html.parser')

        a_elements = soup.find('span', {'id': 'heading'}).find_all('a')
        syllable_links = []
        for a_element in a_elements:
            link = a_element['href']
            if link in syllable_links:
                continue
            syllable_links.append(a_element['href'])

        syllable_dictionary = []
        for syllable_link in syllable_links:
            print 'Crawl link: %s' % (self.crawled_page + syllable_link)
            syllable_html_doc = urllib2.urlopen(self.crawled_page + syllable_link).read()
            syllable_soup = BeautifulSoup(syllable_html_doc, 'html.parser')

            all_p = syllable_soup.find('div', {'id': 'mainBox'}).find_all('p')[1:]
            for p_tag in all_p:
                p_text = p_tag.text
                p_text = p_text.split('\r\n')
                for text in p_text:
                    if not text:
                        continue
                    syllables = text.split('.')[1].lower().split()
                    for syllable in syllables:
                        syllable = syllable.split(',')[0]
                        check_number = any(char.isdigit() for char in syllable)
                        if (syllable not in syllable_dictionary) and (not check_number):
                            syllable_dictionary.append(syllable)

        module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + \
            '/word_recognition'
        path_to_dict = module_path + '/data/syllables_dictionary_1.txt'
        file = open(path_to_dict,"w")
        for syllable in syllable_dictionary:
            file.write(syllable.encode('utf-8') + '\n')
        file.close()

if __name__ == '__main__':
    crawler = SyllableDictionaryCrawler()
    crawler.crawl()
