import unittest
import requests
from bs4 import BeautifulSoup

from DataWrangling.wrangling import df_to_weight_df, calculate_weights, count_by_year
from DataWrangling.wrangling import get_data, clean_data, data_to_df_group
from DataWrangling.wrangling import more_pages_exist, add_to_dict , get_year


class TestWrangling(unittest.TestCase):
    def test_add_to_dict(self):
        """
        Test that it properly adds to dictionary of weights
        """
        d = {}
        author = 'a'
        result = add_to_dict(author, d)
        self.assertTrue(author in result.keys())
        d = {'a': 1}
        author = 'a'
        result = add_to_dict(author, d)
        self.assertEqual(result['a'], 2)
        d = {'b': 1}
        author = 'a'
        result = add_to_dict(author, d)
        self.assertEqual(result['a'], 1)
        self.assertEqual(result['b'], 1)


    def test_get_year(self):
        """
        Test the regex for finding a year in describtion is correct
        """
        pub = ['a', 'b', '(1772)']
        self.assertEqual(get_year(pub), 1772)
        pub = ['a', 'b', 'was (1111) not']
        self.assertEqual(get_year(pub), 1111)
        pub = ['a', 'b', 'was ((1234)) not']
        self.assertEqual(get_year(pub), 1234)
        pub = ['a', 'b', '(asdda)']
        self.assertEqual(get_year(pub), 0)
        pub = ['a', 'b', '()(acbd)(123)(12)(1)(ALEK)(001)(1000)']
        self.assertEqual(get_year(pub), 1000)
        pub = ['a', 'b', '(2000)']
        self.assertEqual(get_year(pub), 2000)
        pub = ['a', 'b', '(0201)(3000)[1234]{1234}']
        self.assertEqual(get_year(pub), 0)


    def test_more_pages_exist(self):
        """
        Test the proper functioning of identifying next pages
        """
        url = 'https://apacz.matinf.uj.edu.pl/jednostki/1-wydzial-matematyki-i-informatyki-uj'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        self.assertTrue(more_pages_exist(soup))
        url = 'https://apacz.matinf.uj.edu.pl/jednostki/1-wydzial-matematyki-i-informatyki-uj?Publication_page=19'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        self.assertFalse(more_pages_exist(soup))
        url = 'https://apacz.matinf.uj.edu.pl/jednostki/5-katedra_algorytmiki'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        self.assertFalse(more_pages_exist(soup))


if __name__ == '__main__':
    unittest.main()
    