# rating file format: userID,ISBN,rating
# book file format: ISBN Title Author Year-Of-Publication Publisher

import os
import csv
import sys

from surprise import Dataset
from surprise import Reader

from collections import defaultdict
import pandas as pd
import numpy as np


class BooksData:

    def __init__(self,path):
        self.ISBN_to_title = {}
        self.title_to_ISBN = {}
        self.ratingsPath = path + 'ratings.csv'
        self.Books = path + 'books.csv'

    def loadBooksData(self):

        # Look for files relative to the directory we are running from
        # os.chdir(os.path.dirname(sys.argv[0]))

        ratingsDataset = 0
        self.ISBN_to_title = {}
        self.title_to_ISBN = {}

        reader = Reader(line_format='user item rating', sep=',', skip_lines=1)

        ratingsDataset = Dataset.load_from_file(self.ratingsPath, reader=reader)

        with open(self.Books, newline='\n') as csvfile:
            bookReader = csv.reader(csvfile)
            next(bookReader)  # Skip header line
            for row in bookReader:
                ISBN = row[0]
                bookTitle = row[1]
                self.ISBN_to_title[ISBN] = bookTitle
                self.title_to_ISBN[bookTitle] = ISBN

        return ratingsDataset

    def getUserRatings(self, user):
        userRatings = []
        df = pd.read_csv(self.ratingsPath, delimiter=',')
        df = df[df['userID'] == user]
        for index, row in df.iterrows():
            userRatings.append((row['ISBN'], row['rating']))
        return userRatings

    def getPopularityRanks(self):
        ratings = defaultdict(int)
        rankings = defaultdict(int)
        with open(self.ratingsPath, newline='\n') as csvfile:
            ratingReader = csv.reader(csvfile)
            next(ratingReader)
            for row in ratingReader:
                ISBN = row[1]
                ratings[ISBN] += 1
        rank = 1
        for bookID, ratingCount in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            rankings[bookID] = rank
            rank += 1
        return rankings

    def getYears(self):
        years = defaultdict(int)
        with open(self.Books, newline='\n') as csvfile:
            bookReader = csv.reader(csvfile)
            next(bookReader)
            for row in bookReader:
                isbn = row[0]
                try:
                    year = int(row[3])
                    if year:
                        years[isbn] = year
                except:
                    years[isbn] = np.NaN
        return years

    def getBookName(self, bookID):
        if bookID in self.ISBN_to_title:
            return self.ISBN_to_title[bookID]
        else:
            return ""

    def getISBN(self, bookName):
        if bookName in self.title_to_ISBN:
            return self.title_to_ISBN[bookName]
        else:
            return 0
