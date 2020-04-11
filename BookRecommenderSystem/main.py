from models.BooksData import BooksData
from surprise import KNNBasic, SVDpp
import numpy as np
import heapq
from collections import defaultdict
from operator import itemgetter


print("Choose Algorithm:")
print("1: SVDpp")
print("2: Collaborative")
al = input()

if al == '2':

    testSubject = '35859'
    k = 10

    # Load our data set and compute the user similarity matrix
    bk = BooksData('data_100/')
    data = bk.loadBooksData()

    trainSet = data.build_full_trainset()

    sim_options = {'name': 'cosine',
                   'user_based': True
                   }

    model = KNNBasic(sim_options=sim_options)
    model.fit(trainSet)
    simsMatrix = model.compute_similarities()
    simsMatrix = np.nan_to_num(simsMatrix)

    # print(simsMatrix)
    # print(type(simsMatrix))

    # Get top N similar users to our test subject
    testUserInnerID = trainSet.to_inner_uid(testSubject)

    if sim_options['user_based']:
        similarityRow = simsMatrix[testUserInnerID]

        similarUsers = []
        for innerID, score in enumerate(similarityRow):
            if innerID != testUserInnerID:
                similarUsers.append((innerID, score))

        kNeighbors = heapq.nlargest(k, similarUsers, key=lambda t: t[1])

        candidates = defaultdict(float)
        for similarUser in kNeighbors:
            innerID = similarUser[0]
            userSimilarityScore = similarUser[1]
            theirRatings = trainSet.ur[innerID]
            for rating in theirRatings:
                candidates[rating[0]] += (rating[1] / 10.0) * userSimilarityScore

    else:
        testUserRatings = trainSet.ur[testUserInnerID]
        kNeighbors = heapq.nlargest(k, testUserRatings, key=lambda t: t[1])

        candidates = defaultdict(float)
        for itemID, rating in kNeighbors:
            similarityRow = simsMatrix[itemID]
            for innerID, score in enumerate(similarityRow):
                candidates[innerID] += score * (rating / 10.0)
    # Get the stuff they rated, and add up ratings for each item, weighted by user similarity

    # Build a dictionary of stuff the user has already read
    read = {}
    # print('\n\nBooks user already read.')
    # print("============================")
    for itemID, rating in trainSet.ur[testUserInnerID]:
        bookID = trainSet.to_raw_iid(itemID)
        # print(bk.getBookName(bookID))
        read[itemID] = 1

    # Get top-rated items from similar users:
    print('\n\nBooks recommended.')
    print("=======================")
    pos = 0
    for itemID, ratingSum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
        if not itemID in read:
            bookID = trainSet.to_raw_iid(itemID)
            print(bk.getBookName(bookID))
            pos += 1
            if (pos > 10):
                break

elif al == '1':
    #SVDpp
    testSubject = '35859'
    bk = BooksData('data_100/')
    def GetAntiTestSetForUser(testSubject,trainSet):
            fill = trainSet.global_mean
            anti_testset = []
            u = trainSet.to_inner_uid(str(testSubject))
            user_items = set([j for (j, _) in trainSet.ur[u]])
            anti_testset += [(trainSet.to_raw_uid(u), trainSet.to_raw_iid(i), fill) for
                                     i in trainSet.all_items() if
                                     i not in user_items]
            return anti_testset
    #Common things
    k = 10

    data = bk.loadBooksData()
    rankings = bk.getPopularityRanks()
    trainSet = data.build_full_trainset()

    model = SVDpp()
    model.fit(trainSet)
    testSet = GetAntiTestSetForUser(testSubject,trainSet)
    predictions = model.test(testSet)
    recommendations = []
    for userID, ISBN, actualRating, estimatedRating, _ in predictions:
        isbn=ISBN
        recommendations.append((isbn, estimatedRating))

    recommendations.sort(key=lambda x: x[1], reverse=True)

    for ratings in recommendations[:k]:
        print(bk.getBookName(ratings[0]))
        #SVDpp predicted rating ratings[1]
        #print(bk.getBookName(ratings[0]), ratings[1])
else:
    print("Wrong Input")
