import unittest
import requests
from bs4 import BeautifulSoup
import pandas as pd
from DataWrangling.wrangling import df_to_weight_df, calculate_weights, count_by_year
from DataWrangling.wrangling import get_data, clean_data, data_to_df_group
from DataWrangling.wrangling import more_pages_exist, add_to_dict, get_year


class TestWrangling(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestWrangling, self).__init__(*args, **kwargs)
        self.data = [['12.','Jerzy Martyna','Resource Allocation in LTE-Unlicensed Femtocell Networks, PRZEGLĄD TELEKOMUNIKACYJNY I WIADOMOŚCI TELEKOMUNIKACYJNE (2018), 839 - 843'],
                      ['11.','Jerzy Martyna',
                      'Performance Analysis of Cognitive Femtocell Network with Ambient RF Energy Harvesting vol. LECTURE NOTES IN COMPUTER SCIENCE, vol. 11118 (2018), "Internet of Things, Smart Spaces and Next Generation Networks and Systems", Springer'],
                      ['10.','Jerzy Martyna',
                      'Analysis of Energy Harvesting in Cognitive Femtocell Radio Network, PRZEGLĄD TELEKOMUNIKACYJNY I WIADOMOŚCI TELEKOMUNIKACYJNE (2018), 312 - 315'],
                      ['9.','Jerzy Martyna',
                      'QoS- and Energy-aware Services Management of Resource in Cloud Computing Environment vol. Communications in Computer and Information Science (2018), "Computer Networks", Springer'],
                      ['8.','Antoni Leon Dawidowicz, Anna Poskrobko',
                      'Asymptotic properties of the Lasota equation in various functional spaces, (2018), "AIP Conference Proceedings 1926", American Institute of Physics'],
                      ['7.','Elżbieta Adamus, Paweł Bogdan, Zbigniew Hajto',
                      'An effective approach to Picard-Vessiot theory and the Jacobian Conjecture, SCHEDAE INFORMATICAE vol. 26 (2017),'],
                      ['6.','Elżbieta Adamus, Paweł Bogdan, Teresa  Crespo, Zbigniew Hajto',
                      'An effective study of polynomial maps, J ALGEBRA APPL vol. Vol. 16, No. 08, 1750141 (2017), 13 pages'],
                      ['5.','Edward Delp, Jarosław Duda, Neeraj Gadgil, Paweł Korus, Khalid  Tahboub',
                      'Image-Like 2D Barcodes Using Generalizations of the Kuznetsov–Tsybakov Problem, IEEE T INF FOREN SEC vol. volume 11 issue 4 (2016), 691-703'],
                      ['4.','Marian Jabłoński, A Ozga',
                      'Determining the Distribution of Values of Stochastic Impulses Acting on a Discrete System in Relation to Their Intensity , ACTA PHYS POL A vol. 121 (2012), A174-A178'],
                      ['3.','Marian Jabłoński, T Korbiel, A Ozga, P Pawlik',
                      'Determining the Distribution of Stochastic Impulses Acting on a High Frequency System through an Analysis of Its Vibrations, ACTA PHYS POL A vol. 119 (2011), 977-980'],
                      ['2.','Marian Jabłoński, A Ozga',
                      'Distribution of Stochastic Impulses Acting on an Oscillator as a Function of Its Motion , ACTA PHYS POL A vol. 118 (2010),  74-77'],
                      ['1.','Marian Jabłoński, A Ozga',
                      'Statistical Characteristics of the Damped Vibrations of a String Excited by Stochastic Forces , ARCH ACOUST vol. 34 (2009),  601-612']]
        headers = ['author', 'coauthor', 'year']
        d = [['Antoni Leon Dawidowicz','Anna Poskrobko',2018],
            ['Elżbieta Adamus', 'Paweł Bogdan', 2017
            ],['Elżbieta Adamus', 'Zbigniew Hajto', 2017
            ],['Paweł Bogdan','Zbigniew Hajto',2017
            ],['Elżbieta Adamus','Paweł Bogdan',2017
            ],['Elżbieta Adamus','Teresa Crespo',2017
            ],['Elżbieta Adamus', 'Zbigniew Hajto', 2017
            ],['Paweł Bogdan','Teresa Crespo', 2017
            ],['Paweł Bogdan','Zbigniew Hajto',2017
            ],['Teresa Crespo','Zbigniew Hajto',2017
            ],['Edward Delp','Jarosław Duda',2016
            ],['Edward Delp','Neeraj Gadgil',2016
            ],['Edward Delp', 'Paweł Korus',2016
            ],['Edward Delp', 'Khalid Tahboub',2016
            ],['Jarosław Duda', 'Neeraj Gadgil',2016
            ],['Jarosław Duda', 'Paweł Korus', 2016
            ],['Jarosław Duda', 'Khalid Tahboub', 2016
            ],['Neeraj Gadgil', 'Paweł Korus', 2016
            ],['Neeraj Gadgil', 'Khalid Tahboub', 2016
            ],['Paweł Korus', 'Khalid Tahboub', 2016
            ],['Marian Jabłoński','A Ozga',2012
            ],['Marian Jabłoński','T Korbiel',2011
            ],['Marian Jabłoński','A Ozga',2011
            ],['Marian Jabłoński','P Pawlik',2011
            ],['T Korbiel', 'A Ozga', 2011
            ],['T Korbiel','P Pawlik',2011],
            ['A Ozga','P Pawlik',2011],
            ['Marian Jabłoński','A Ozga',2010],
            ['Marian Jabłoński','A Ozga',2009]]
        self.df = pd.DataFrame(d, columns=headers)


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


    def test_clean_data(self):
        """
        Test that we are properly preparing data and not loosing important information
        """
        self.assertEqual(len(self.data), 12)
        for row in self.data:
            self.assertEqual(len(row), 3)


    def test_calculate_weights(self):
        """
        Test that the function calculating the number of
         publications written by an author works correctly
        """
        weights1 = calculate_weights(self.data, 0, 2019)
        #check calculating publications done alone 
        self.assertEqual(weights1['Jerzy Martyna'], 4)

        #check date filtering
        weights = calculate_weights(self.data, 2011, 2011)
        self.assertEqual(weights['Marian Jabłoński'], 1)

        #check calculating publications with many authors
        self.assertEqual(weights1['Marian Jabłoński'], weights1['A Ozga'])


    def test_data_to_df_group(self):
        """
        Testing that transforming data to author, coauthor, year
        works correctly
        """
        df = data_to_df_group(self.data)
        #generally works well
        self.assertEqual(len(df[df.year == 2009]), 1) 
        # not looses information about authors
        self.assertEqual(len(df[(df.author == 'A Ozga') | (df.coauthor == 'A Ozga')]), 6)
        # forgets work done alone
        self.assertEqual(len(df[df.author == 'Jerzy Martyna']), 0)
        #remembers all data from complex publications
        self.assertEqual(len(df[(df.author == 'Edward Delp') & (df.coauthor == 'Jarosław Duda')]), 1)
        self.assertEqual(len(df[(df.author == 'Edward Delp') & (df.coauthor == 'Neeraj Gadgil')]), 1)
        self.assertEqual(len(df[(df.author == 'Edward Delp') & (df.coauthor == 'Paweł Korus')]), 1)
        self.assertEqual(len(df[(df.author == 'Edward Delp') & (df.coauthor == 'Khalid  Tahboub')]), 1)
        self.assertEqual(len(df[(df.author == 'Jarosław Duda') & (df.coauthor == 'Neeraj Gadgil')]), 1)
        self.assertEqual(len(df[(df.author == 'Jarosław Duda') & (df.coauthor == 'Paweł Korus')]), 1)
        self.assertEqual(len(df[(df.author == 'Jarosław Duda') & (df.coauthor == 'Khalid  Tahboub')]), 1)
        self.assertEqual(len(df[(df.author == 'Neeraj Gadgil') & (df.coauthor == 'Paweł Korus')]), 1)
        self.assertEqual(len(df[(df.author == 'Neeraj Gadgil') & (df.coauthor == 'Khalid  Tahboub')]), 1)
        self.assertEqual(len(df[(df.author == 'Paweł Korus') & (df.coauthor == 'Khalid  Tahboub')]), 1)

    def test_count_by_year(self):
        """
        Testing that the function counting how many publications an author wrote
        works properly
        """
        #only one in only one year
        years, counts = count_by_year(self.data, 'P Pawlik')
        self.assertEqual(years, [2011])
        self.assertEqual(counts, [1])
        # many in one year
        years, counts = count_by_year(self.data, 'Paweł Bogdan')
        self.assertEqual(years, [2017])
        self.assertEqual(counts, [2])
        #many years    
        years, counts = count_by_year(self.data, 'Marian Jabłoński')
        self.assertEqual(years, [2009, 2010, 2011, 2012])
        self.assertEqual(counts, [1, 1, 1, 1])
        #zero
        years, counts = count_by_year(self.data, 'Adam Roman')
        self.assertEqual(years, [])
        self.assertEqual(counts, [])

    def test_df_to_weigh_df(self):
        """
        Testing that the function transforming data to author-coauthor-weight 
        dataframe is working as intended
        """
        df = df_to_weight_df(self.df)
        # not loosing information
        s = df.weight.sum()
        self.assertEqual(s, len(self.df))
        # should be zero
        self.assertEqual(len(df[df.author == 'Zbigniew Hajto']), 0)
        #should be one
        self.assertEqual(len(df[df.coauthor == 'T Korbiel']), 1)
        #should be many (sum as author and coauthor)
        self.assertEqual(len(df[(df.coauthor == 'Paweł Korus') | (df.author == 'Paweł Korus')]), 4)

   
if __name__ == '__main__':
    unittest.main()
    