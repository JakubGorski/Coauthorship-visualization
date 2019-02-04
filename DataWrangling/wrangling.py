"""This script contains methods needed for data downloading and wrangling"""
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup


def get_data(unit='1-wydzial_matematyki_i_informatyki_uj'):
    """function takes as a parameter the unit of department (default is the whole department)
    from that unit / whole department gets the data about publications
    """
    publication_page = 1
    publications = []
    url = 'https://apacz.matinf.uj.edu.pl/jednostki/' + unit\
    + '?Publication_page=' + str(publication_page)
    page = requests.get(url)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, 'html.parser')
        publications = soup.findAll("div", {'class': "row-fluid"})

        while more_pages_exist(soup):
            publication_page += 1
            url = 'https://apacz.matinf.uj.edu.pl/jednostki/' + unit\
            + '?Publication_page=' + str(publication_page)
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')
            publications += soup.findAll("div", {'class': "row-fluid"})

    return publications


def more_pages_exist(soup):
    """function takes as a parameter the current page of publications and checks
    if those are all or more publications exists (pager)
    """
    summary = soup.findAll("div", {'class': "summary"})
    line = summary[0].get_text()
    number_last = line[line.find('-')+1 : line.find(' ')]
    number_total = line[line.rfind(' ')+1 : line.rfind('.')]

    return number_last != number_total


def clean_data(data):
    """function accepts the list of data about the publications and keeps only the relevant parts"""
    data_list = []
    for row in data:
        text = row.get_text()
        text_list = [s.strip() for s in text.splitlines() if s != '']
        while '' in text_list:
            text_list.remove('')
        if len(text_list) > 3:
            text_list[2:len(text_list)] = [''.join(text_list[2:len(text_list)])]
        data_list.append(text_list)

    return data_list


def data_to_df_group(data):
    """function accepts the list of relevant data and makes a dataftame out of it,
     forgetting publications done alone
     """
    future_df = []
    row = []
    for publication in data:
        authors_list = publication[1].split(',')
        year = get_year(publication)
        for i in range(len(authors_list)):
            author = authors_list[i].lstrip()
            authors = authors_list[i + 1:]
            for coauthor in authors:
                row = [author]
                row.append(coauthor.lstrip())
                row.append(year)
                future_df.append(row[:])

    return pd.DataFrame(future_df, columns=['author', 'coauthor', 'year'])


def df_to_weight_df(dataframe):
    """function accepts pandas dataframe with cleaned data and adds a column with weight,
    which is number of publications written together by a pair of author-coauthor
    """
    author_dict = {}
    for _, row in dataframe.iterrows():
        pair = tuple(row[:2])
        if pair in author_dict:
            author_dict[pair] += 1
        else:
            author_dict[pair] = 1
    data = []
    for key, value in author_dict.items():
        row = [author for author in list(key)]
        row.append(value)
        data.append(row[:])

    return pd.DataFrame(data, columns=['author', 'coauthor', 'weight'])


def calculate_weights(cleaned_data, start_date=0, end_date=2019):
    """function calculates the number of publications by author(weights)
    returns dictionary with author names as keys and # of publications as value
    """
    authors_publications_dic = {}
    for publication in cleaned_data:
        authors_list = publication[1].split(',')
        year = get_year(publication)
        if (year >= start_date) & (year <= end_date):
            for author in authors_list:
                add_to_dict(author.lstrip(), authors_publications_dic)
    return authors_publications_dic


def add_to_dict(author, author_dict):
    """Helper function for adding to dictionary"""
    if author not in author_dict:
        author_dict[author] = 1
    else:
        author_dict[author] += 1
    return author_dict


def get_year(publication):
    """Helper function for extracting year from publication
    description on website, returns year value
    """
    try:
        found = re.search(r'\((1|2)\d\d\d\)', publication[2]).group(0)
        found = int(found[1:5])
    except AttributeError:
        found = 0
    year = found
    return year


def count_by_year(data, author):
    """counts the number of publications by selected author
    by years, returns list of years and # of publications in that year
    """
    years_counts_dict = {}
    years = []
    for publication in data:
        authors_list = publication[1].split(',')
        for i in range(len(authors_list)):
            authors_list[i] = authors_list[i].lstrip()
        year = get_year(publication)
        if year >= 1960:
            if author in authors_list:
                add_to_dict(year, years_counts_dict)
        years = [year for year in years_counts_dict.keys()]
        values = [value for value in years_counts_dict.values()]

    return years, values

def shorten_name(name):
    """helper to make name fully visible in legend"""
    name_surname = name.split()
    new_name = name_surname[0][0] + '.' + name_surname[1]
    return new_name
