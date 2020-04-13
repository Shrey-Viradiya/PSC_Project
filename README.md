# PSC_Project
PSC project submission repository.

Students:
1. Sunidhi Tandel (18BCE239)
2. Tirth Patel (18BCE245)
3. Shrey Viradiya (18BCE259)

## Introduction:

In the modern technological era, Recommandation system and Sentiment Analysis are leading in the manners by which content-serving sites like Facebook, Amazon, Spotify,Netflix Flipkart or social medias like Instagram, Facebook or literally any web application interact with thier user. All the web content based applications mentioned above implemented Recommedation System and sentiment analysis on the product reviews they get.
**Our django based LMS web application manages the catalog of a library along with recommendations as well as sentimental analysis.** 

## Description:

In this repository, **3 directories** are present...

### 1-SentimentAna:
Contains a ipynb file showing our work on Sentiment Analysis.

In this, we used **Textblob** library built upon **nltk** environment. TextBlob is a Python library for processing textual data. It provides a simple API for diving into common natural language processing (NLP) tasks such as part-of-speech tagging, noun phrase extraction, sentiment analysis, classification, translation, and more.

The sentiment property of Textblob returns a namedtuple of the form **Sentiment(polarity, subjectivity)**. The polarity score is a float within the range **[-1.0, 1.0]**. The subjectivity is a float within the range **[0.0, 1.0]** where 0.0 is very objective and 1.0 is very subjective.

So if the polarity of a sentiment is greater than 0, then sentiment is consider as positive otherwise negative. If the Sentiment is positive then we are giving **5 ratings** and if it is negative then we are giving **rating 1** to the book based on the review given by user. Then finally taking the average of all ratings we are generating automatic rating of a book based on the review given by the users!

**Limitation -** This a approach fails when the sentiment is too objective!

### 2-BookRecommenderSystem:
Contains our work and dataset for Book Recommendation.
We have used colloborative filtering. This approach find users who have given similar ratings to the same book.

Algorithms included in BookRecommenderSystem : 1. Matrix factorization methods such as SVD and SVD++(Netflix prize winner algo)
                                               2. K-Nearest-Neighbours user based colloborative filtering
                                               3. K-Nearest-Neighbours item based colloborative filtering

Surprise python library is used to generate reccomandation. It provides a nice API and a nice pipeline for recommender systems. We used the Surprise library in order to do matrix factorization on the user-item matrix.

kNN is a machine learning algorithm to find clusters of similar users based on common book ratings, and make predictions using the average rating of top-k nearest neighbors. The SVD algorithm of Surprise uses Gradient Descent to optimize the RMSE . **The main difference is that Surprise does not assume that unrated items are rated as 0.**

We integrated KNN user based CF and SVD in our LMS system.

Analysis of algorithms is done in SVDBakeOff.py file.
It computes RMSE,MAE,Hitrate,Coverage etc.

**Limitation -** Item based colloborative filtering for large dataset requires high computing power.

### 3-LMS: 
Contains a django project of Library Management System. This django project has integrated Sentiment Analysis and Book Recommendations which are described in the previos directories.

## Notice: 
- ### Book Recommendation System might take a lots of computing power. If large computing power is not available, DO NOT RUN THE CODE ON LARGE DATASET !!
- #### A video has been included in the repository to demonstrate the project. 
- #### First two directories can be run with out any additional requirements after installing required libraries.
- #### LMS can be installed in the successfully in your system. To run this project you must have PostgreSQL DBMS in your system (or any other which is supported by django). You must link the Database with project in settings.py file in LMS subdirectory in LMS directory.
- #### After completing this integration we have data of nearly 9800 books. Which you have to add in the database. THIS IS TIME CONSUMING STEP.

## Videos
- We uploaded 2 videos.
1. First video contains the explaination and demonstration of our project.
2. Second video is much smaller. This video does not exaplain any thing. We only showed integrated SVD algorithm which was done after recording first video
