# ----------------------------------------------------------------------------------------------------------------------
# Author:         Divya Shrivastava
# Date:           03/31/2020
# Class:          CMSC 416 NLP
# File:           sentiment.py
# Function:       The purpose of this program is to create a Python program that will take as input a training file
#                 containing text tagged with sentiment ID's and a file containing text that needs to be tagged. In
#                 order to execute this program, a decision list must be created that is based on the absolute log
#                 probability of one sense given a feature divided by the probability of the second sense given the
#                 feature. After analyzing the training data, this program should take each word in the test data and
#                 assign the sentiment ID based off a ranking list of which sentiment ID is most seen with feature
#                 types. If a word is not assigned a sentiment ID in the test data, automatically assign the tag the
#                 sentiment ID used the most in the training data. The accuracy of the sentiment IDs tagged in a given
#                 test file is 72.96%. MFSB for my sentiment.py is 68.67%.
#
#                 The following is an example program input and output:
#                 command line prompt: sentiment.py sentiment-train.txt sentiment-test.txt > my-sentiment-answers.txt
#                 output: a file containing text that had been assigned sentiment IDs.
#
#                 The user must compile the program and input three arguments - the file that contains text that is
#                 already tagged with sentiment IDs, the file that contains text that needs to be tagged, and the file
#                 to which the tagged text will eventually be output to. For this program, I started off by
#                 reading in the training data first and parsing through it. I separated each sentiment ID into a
#                 dictionary with both the sentiment IDs and context. Then, I split the context to analyze the bag of
#                 words feature. A nested dictionary was created for sentimentIDDict in which the outer dictionary,
#                 sentiment ID, was linked to the features. Once the models in this dictionary and the ranking list
#                 dictionary were created after parsing through the entire training data, the test data was read in,
#                 parsed, and assigned sentiment IDs. This happened by comparing features in the test data to those in
#                 the ranking list dictionary. The word found in the ranking list with the highest rank was assigned the
#                 sentiment ID. As each sentiment ID was assigned to an instance ID, it was printed out to the file.
# -----------------------------------------------------------------------------------------------------------------------
import math
import operator
import re
import sys

# Global variable
use_stop_word_removal = True
stopWordList = ["a", "about", "after", "all", "also", "an", "and", "are", "as", "at", "back", "be", "because",
                         "been", "before", "being", "between", "but", "by", "can", "could", "do", "even", "first",
                         "for", "from", "get", "good", "had", "has", "have", "he", "her", "his", "how", "i", "if",
                         "in", "into", "is", "it", "its", "just", "look", "make", "many", "more", "most", "much",
                         "must", "new", "no", "not", "now", "of", "off", "on", "one", "only", "open", "or", "other",
                         "our", "out", "over", "own", "people", "she", "so", "some", "than", "that", "the", "their",
                         "them", "then", "there", "they", "this", "those", "through", "time", "to", "two", "up", "us",
                         "very", "was", "way", "we", "well", "were", "what", "when", "which", "while", "who", "will",
                         "with", "would", "years", "you", "your", "aacute", "amp", "bquo", "ccaron", "dollar", "eacute",
                         "equo", "hellip", "iacute", "icirc", "ins", "lsqb", "mdash", "ndash", "oacute", "oslash",
                         "rcaron", "rsqb", "scaron", "uuml", "yacute", "zcaron"]

# XML Parser to read in file and store instance id in dictionary corresponding to sense id and corresponding to context
def Read_XML_File(file_path):
    openTrainTest = open(file_path, encoding="utf8")
    lines = openTrainTest.readlines()

    instance_id = None
    sentiment = None
    context = ""

    trainDict = {}

    for i in range(len(lines)):
        line = lines[i]
        line = line.rstrip()

        # Capture instance ID
        if re.search(r'^\<instance id=', line):
            line = re.sub(r'^\<instance id=\"|\"\>', "", line)
            instance_id = line

        # Capture sentiment
        if instance_id is not None and re.search(r'\<answer instance=\"', line):
            line = re.sub(re.escape('<answer instance=\"' + instance_id + "\"") + r'|sentiment=\"|\"/\>', "", line)
            sentiment = line

        # Capture context of instance
        if instance_id is not None and re.search('^\<context\>', line):
            i += 1
            while not re.search(r'\<\/context\>', lines[i]):
                context += lines[i].rstrip() + " "
                i += 1

        # Store elements in training dictionary and clear local variables if found
        if instance_id is not None and context != "":
            if instance_id not in trainDict:
                trainDict[instance_id] = {}

            # Test data does not contain sentiment information
            if sentiment is not None:
                trainDict[instance_id]["Sentiment"] = sentiment

            trainDict[instance_id]["Context"] = context

            # Clear variables for next instance data
            instance_id = None
            sentiment = None
            context = ""

    return trainDict


# Parse context to clean it up for analyzing
def Clean_Context(context):
    context = re.sub(r'\<s\>|\<\/s\>|\<p\>|\<\/p\>|\<@\>|\.|\,|\"|\\-|\\--', '', context)

    # Stop Word Removal
    if use_stop_word_removal == True:
        for token in context.split(" "):
            if token in stopWordList:
                context = re.sub( r'\b' + token + r'\b', '', context)
    return context

def main():
    trainText = sys.argv[1]
    testText = sys.argv[2]
    modelFile = sys.argv[3]
    modelFile = open(modelFile, "w")

    trainDict = Read_XML_File(trainText)
    testDict = Read_XML_File(testText)
    sentimentDict = {}
    unigramTable = {}
    totalCount = 0
    featuresDecisionList = []
    rankingList = {}
    positiveCount = 0
    negativeCount = 0
    mfsb = ""

    # Analyze each instance in the training data
    for instance_id in trainDict:

        sentiment = trainDict[instance_id]["Sentiment"]
        context = trainDict[instance_id]["Context"]

        # Keep count of whether sentiment is positive or negative to determine MFSB
        if re.search(r'positive', sentiment):
            positiveCount += 1
        elif re.search(r'negative', sentiment):
            negativeCount += 1

        context = Clean_Context(context)
        featureWords = context.split()

        # Analyze each word in context
        for word in featureWords:
            featureIndex = featureWords.index(word)

            if sentiment not in sentimentDict:
                sentimentDict[sentiment] = {}

            if word not in sentimentDict[sentiment]:
                sentimentDict[sentiment][word] = {}
                sentimentDict[sentiment][word] = 0

            if word not in unigramTable:
                unigramTable[word] = 0

            sentimentDict[sentiment][word] += 1
            unigramTable[word] += 1
            totalCount += 1

    # Determine higher sense probability (MFSB)
    if(positiveCount >= negativeCount):
        mfsb = "positive"
    else:
        mfsb = "negative"

    # Calculate probability of Count(Sense | feature) / Count(feature)
    for sentiment_id in sentimentDict:
        for wordFeature in sentimentDict[sentiment_id]:
            numerator = sentimentDict[sentiment_id][wordFeature]
            denominator = unigramTable[wordFeature]
            probability = numerator / denominator
            sentimentDict[sentiment_id][wordFeature] = probability

            # Create a features list and add to it
            if wordFeature not in featuresDecisionList:
                featuresDecisionList.append(wordFeature)

    # Rank the list
    for feature in featuresDecisionList:
        # compare sense 1 prob with sense 2 prob
        compareProbabilities = []
        maxProbability = 0
        sentiment = ""

        # getting probability value based off of feature given its sense
        for currSentiment in sentimentDict:
            currentProbability = 0

            if feature in sentimentDict[currSentiment]:
                currentProbability = sentimentDict[currSentiment][feature]

            if currentProbability > maxProbability:
                maxProbability = currentProbability
                sentiment = currSentiment

            compareProbabilities.append(currentProbability)

        rankValue = None

        if compareProbabilities[0] != 0 and compareProbabilities[1] != 0:
            rankValue = abs(math.log(compareProbabilities[0] / compareProbabilities[1]))
        else:
            rankValue = abs(math.log(1))

        # Store values in decision list for ranking
        if rankValue is not None:
            rankingList[sentiment + " -> " + feature] = rankValue

    # sort ranking list in descending order
    rankingList = dict( sorted(rankingList.items(), key=operator.itemgetter(1),reverse=True))

    # create model to print to my-model.txt
    for prediction in rankingList:
        elements = prediction.split("->")
        feature = elements[1]
        sentiment = elements[0]
        rankValue = rankingList[prediction]
        sentiment.strip()

        # if features are certain feature types, print to my-model.txt accordingly
        modelFile.write("Feature: \"" + feature + "\" -> Predicts: " + sentiment + " -> Rank: " + str(rankValue) + "\n")

    modelFile.close()

    # Apply model created from training data to assign sentiment to test data
    for instance_id in testDict:
        testContext = testDict[instance_id]["Context"]
        testContext = Clean_Context( testContext )
        testFeatureWords = testContext.split()

        currSentiment = None
        currFeature   = None
        highestRank   = 0.0

        for testWord in testFeatureWords:
            # compare each feature to element in ranking list and assign sentiment accordingly
            for prediction in rankingList:
                element   = prediction.split(" -> ")
                sentiment = element[0]
                feature   = element[1]
                rankValue = rankingList[prediction]

                # keep checking until word with highest rank value is utilized to assign sentiment ID
                if feature == testWord and rankValue > highestRank:
                    currSentiment = sentiment
                    currFeature   = testWord
                    highestRank   = rankValue

        # assign test sentiment the most frequent ID if it is not assigned
        if currSentiment == None:
            currSentiment = mfsb

        # assign sentiment to instance id
        testDict[instance_id]["Sentiment"] = currSentiment
        print("<answer instance=\"" + instance_id + "\" sentiment=\"" + currSentiment + "\"/>")


# call main method
if __name__ == "__main__":
    main()