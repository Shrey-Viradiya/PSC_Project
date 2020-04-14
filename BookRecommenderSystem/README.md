## Recommendation Structure


**Datasets**


**Datafiles :**

    1. books.csv 

    2. ratings.csv

    3. users.csv
    
    
Booksdata.py load required data


**Data Preprocessing (cleaning) :**


Data preprocessing is one of the most significant part of any Data Science project. 
We analyzed and cleaned our data using pandas library .
Small well processed dataset is used in LMS web application.


**Evaluation of Algorithm :**


1. kNN user based CF : 

   Computes cosine similarity matrix between users, cluster nearest neighbour and provide top N recommendations.

2. SVD : 

    It is a matrix factorization technique that is usually used to reduce the number of features of a data set by reducing space dimension from n features to k.
    It minimize error with Stochastic Gradient Descent (SGD) and provide top N recommendations.

3. SVD++ :

    The SVD++ algorithm is an extension of SVD that takes into account implicit ratings.


*Surprise library used to make recommandation.*
