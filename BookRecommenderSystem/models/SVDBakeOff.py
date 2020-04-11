from models.BooksData import BooksData
from surprise import SVD, SVDpp
from surprise import NormalPredictor
from models.Evaluator import Evaluator

import random
import numpy as np

def LoadBookData():
    bk = BooksData('../data_100/')
    print("Loading movie ratings...")
    data = bk.loadBooksData()
    print("\nComputing movie popularity ranks so we can measure novelty later...")
    rankings = bk.getPopularityRanks()
    return (bk, data, rankings)

np.random.seed(0)
random.seed(0)

# Load up common data set for the recommender algorithms
(bk, evaluationData, rankings) = LoadBookData()

# Construct an Evaluator to, you know, evaluate them
evaluator = Evaluator(evaluationData, rankings)

# SVD
SVD = SVD()
evaluator.AddAlgorithm(SVD, "SVD")

# SVD++
SVDPlusPlus = SVDpp()
evaluator.AddAlgorithm(SVDPlusPlus, "SVD++")

# Just make random recommendations
Random = NormalPredictor()
evaluator.AddAlgorithm(Random, "Random")

# Fight!
evaluator.Evaluate(False)

evaluator.SampleTopNRecs(bk, testSubject=276680)
