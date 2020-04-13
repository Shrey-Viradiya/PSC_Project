# PSC_Project
PSC project submission repository.

Students:
1. Sunidhi Tandel (18BCE239)
2. Tirth Patel (18BCE245)
3. Shrey Viradiya (18BCE259)

## Introduction:

In the modern technological era, all the web content based applications like Netflix, Amazon, Flipkart or social medias like Instagram, Facebook or literally any web application implemented Recommedation System and sentiment analysis on the product reviews they get.

## Description:

In this repository, 3 directories are present...

**SentimentAna:** Contains a ipynb file showing our work on Sentiment Analysis.

In this, we used **Textblob** library built upon **nltk** environment. TextBlob is a Python library for processing textual data. It provides a simple API for diving into common natural language processing (NLP) tasks such as part-of-speech tagging, noun phrase extraction, sentiment analysis, classification, translation, and more.

The sentiment property of Textblob returns a namedtuple of the form Sentiment(polarity, subjectivity). The polarity score is a float within the range [-1.0, 1.0]. The subjectivity is a float within the range [0.0, 1.0] where 0.0 is very objective and 1.0 is very subjective.

So if the polarity of a sentiment is greater than 0, then sentiment is consider as positive otherwise negative. If the Sentiment is positive then we are giving **5 ratings** and if it is negative then we are giving **rating 1** to the book based on the review given by user.

**Limitation -** This a approach fails when the sentence is too objective!

**BookRecommenderSystem:** Contains our work and dataset for Book Recommendation.

**LMS:** Contains a django project of Library Management System. This django project has integrated Sentiment Analysis and Book Recommendations which are described in the previos directories.

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
