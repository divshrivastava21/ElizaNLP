# ----------------------------------------------------------------------------------------------------------------------
# Author:         Divya Shrivastava
# Date:           03/30/2020
# Class:          CMSC 416 NLP
# File:           wsd.py
# Function:       The purpose of this program is to create a Python program that will take as input a training file
#                 containing text tagged with sense ID's and a file containing text that needs to be tagged. In
#                 order to execute this program, a decision list must be created that is based on the absolute log
#                 probability of one sense given a feature divided by the probability of the second sense given the
#                 feature. After analyzing the
#                 training data, this program should take each word in the test data and assign the sense ID based off
#                 a ranking list of which sense ID is most seen with feature types. If a word is not assigned a sense
#                 ID in the test data, automatically assign the tag the sense ID used the most in the training data.
#                 The accuracy of the sense IDs tagged in a given test file is 84.25%. MSFB for my wsd.py is around 42%.
#
#                 The following is an example program input and output:
#                 command line prompt: wsd.py line-train.txt line-test.txt > my-line-answers.txt
#                 output: a file containing text that had been assigned sense IDs.
#
#                 The user must compile the program and input three arguments - the file that contains text that is
#                 already tagged with sense IDs, the file that contains text that needs to be tagged, and the file to
#                 which the tagged text will eventually be output to. For this program, I started off by
#                 reading in the training data first and parsing through it. I separated each instance ID into a
#                 dictionary with both the senseIDs and context. Then, I split the context to analyze the different
#                 features. The features I used described within Yarowsky's paper are 1 to the left of "line" (-1), 1 to
#                 the right (-1), 2 to the left (-2), 2 to the right (+2), 1 to the left and 1 to the right (-1/+1), and
#                 k window size of 2. A nested dictionary was created for senseIDDict in which the outer dictionary,
#                 sense ID, was linked to the features.Once the models in this dictionary and the ranking list
#                 dictionary were created after parsing through the entire training data, the test data was read in,
#                 parsed, and assign sense IDs. This happened by comparing features in the test data to those in the
#                 ranking list dictionary. The first feature found in the ranking list was assigned the sense ID. As
#                 each sense ID was assigned to an instance ID, it was printed out to the file.
# -----------------------------------------------------------------------------------------------------------------------
import math
import operator
import re
import sys

# Global variable
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
    sense_id = None
    context = ""

    trainDict = {}

    for i in range(len(lines)):
        line = lines[i]
        line = line.rstrip()

        # Capture instance ID
        if re.search(r'^\<instance id=', line):
            line = re.sub(r'^\<instance id=\"|\"\>', "", line)
            instance_id = line

        # Capture Sense ID
        if instance_id is not None and re.search(r'\<answer instance=\"', line):
            line = re.sub(re.escape('<answer instance=\"' + instance_id + "\"") + r'|senseid=\"|\"/\>', "", line)
            sense_id = line

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

            # Test data does not contain sense id information
            if sense_id is not None:
                trainDict[instance_id]["Sense_ID"] = sense_id

            trainDict[instance_id]["Context"] = context

            # Clear variables for next instance data
            instance_id = None
            sense_id = None
            context = ""

    return trainDict


# Parse context to clean it up for analyzing
def Clean_Context(context):
    context = re.sub(r'\<s\>|\<\/s\>|\<p\>|\<\/p\>|\<@\>|\.|\,|\"|\\-|\\--', '', context)

    # Stop Word Removal
    for token in context.split(" "):
        if token in stopWordList:
            context = re.sub( r'\b' + token + r'\b', '', context)
    return context


def main():
    trainText = sys.argv[1]
    testText = sys.argv[2]
    modelFile = sys.argv[3]
    modelFile = open(modelFile, "w")

    kWindowSize = 2
    trainDict = Read_XML_File(trainText)
    testDict = Read_XML_File(testText)
    senseIDDict = {}
    unigramTable = {}
    totalCount = 0
    featuresDecisionList = []
    rankingList = {}
    testSenseID = ""
    phoneCount = 0
    productCount = 0
    totalCounter = 0
    higherSenseMSFB = ""

    # Analyze each instance in the training data
    for instance_id in trainDict:

        sense_id = trainDict[instance_id]["Sense_ID"]
        context = trainDict[instance_id]["Context"]

        # Keep count of whether sense ID is phone or product to determine MSFB
        if re.search(r'phone', sense_id):
            phoneCount += 1
            totalCounter += 1
        elif re.search(r'product', sense_id):
            productCount += 1
            totalCounter += 1

        context = Clean_Context(context)
        featureWords = context.split()

        # Analyze each word in context
        for word in featureWords:

            regexp = re.compile(r'^\<head')
            featureIndex = featureWords.index(word)

            # If word is <head>line</head>
            if (regexp.search(word)):
                if sense_id not in senseIDDict:
                    senseIDDict[sense_id] = {}

                # Word To Left (-1), Store in SenseIDDict and unigramTable
                if featureIndex - 1 >= 0:
                    word_to_left = "L: " + featureWords[featureIndex - 1]

                    if word_to_left not in senseIDDict[sense_id]:
                        senseIDDict[sense_id][word_to_left] = {}
                        senseIDDict[sense_id][word_to_left] = 0

                    if word_to_left not in unigramTable:
                        unigramTable[word_to_left] = 0

                    senseIDDict[sense_id][word_to_left] += 1
                    unigramTable[word_to_left] += 1

                # Word To Right (+1), Store in SenseIDDict and unigramTable
                if featureIndex + 1 < len(featureWords):
                    word_to_right = "R: " + featureWords[featureIndex + 1]

                    if word_to_right not in senseIDDict[sense_id]:
                        senseIDDict[sense_id][word_to_right] = {}
                        senseIDDict[sense_id][word_to_right] = 0

                    if word_to_right not in unigramTable:
                        unigramTable[word_to_right] = 0

                    senseIDDict[sense_id][word_to_right] += 1
                    unigramTable[word_to_right] += 1

                # -2 Words To Left, Store in SenseIDDict and unigramTable
                if featureIndex - 2 >= 0:
                    two_to_left = "2L: " + " ".join(featureWords[featureIndex - 2:featureIndex])

                    if two_to_left not in senseIDDict[sense_id]:
                        senseIDDict[sense_id][two_to_left] = {}
                        senseIDDict[sense_id][two_to_left] = 0

                    if two_to_left not in unigramTable:
                        unigramTable[two_to_left] = 0

                    senseIDDict[sense_id][two_to_left] += 1
                    unigramTable[two_to_left] += 1

                # +2 Words To Right, Store in SenseIDDict and unigramTable
                if featureIndex + 2 < len(featureWords):
                    two_to_right = "2R: " + " ".join(featureWords[featureIndex + 1:featureIndex + 3])

                    if two_to_right not in senseIDDict[sense_id]:
                        senseIDDict[sense_id][two_to_right] = {}
                        senseIDDict[sense_id][two_to_right] = 0

                    if two_to_right not in unigramTable:
                        unigramTable[two_to_right] = 0

                    senseIDDict[sense_id][two_to_right] += 1
                    unigramTable[two_to_right] += 1

                # -1 and +1 Surrounding Target Term, Store in SenseIDDict and unigramTable
                if featureIndex - 1 >= 0 and featureIndex + 1 < len(featureWords):
                    words_left_and_right = "LR: " + featureWords[featureIndex - 1] + " " + featureWords[
                        featureIndex + 1]

                    if words_left_and_right not in senseIDDict[sense_id]:
                        senseIDDict[sense_id][words_left_and_right] = {}
                        senseIDDict[sense_id][words_left_and_right] = 0

                    if words_left_and_right not in unigramTable:
                        unigramTable[words_left_and_right] = 0

                    senseIDDict[sense_id][words_left_and_right] += 1
                    unigramTable[words_left_and_right] += 1

                # Calculate index of surrounding terms given k Window Size
                beginningIndex = featureIndex - kWindowSize
                stopIndex = featureIndex + kWindowSize

                if beginningIndex < 0:
                    beginningIndex = 0
                if stopIndex > len(featureWords):
                    stopIndex = len(featureWords)

                windowFeatures = slice(beginningIndex, stopIndex + 1, 1)

                # Store counts in dictionaries given k Window
                for windowFeature in featureWords[windowFeatures]:

                    if not re.search(r'\<head', windowFeature):
                        windowFeature = "W: " + windowFeature

                        if sense_id not in senseIDDict:
                            senseIDDict[sense_id] = {}

                        if windowFeature not in senseIDDict[sense_id]:
                            senseIDDict[sense_id][windowFeature] = {}
                            senseIDDict[sense_id][windowFeature] = 0

                        if windowFeature not in unigramTable:
                            unigramTable[windowFeature] = 0

                        senseIDDict[sense_id][windowFeature] += 1
                        unigramTable[windowFeature] += 1
                        totalCount += 1

    # Determine higher sense probability (MSFB)
    if(productCount >= phoneCount):
        higherSenseMSFB = "product"
    else:
        higherSenseMSFB = "phone"

    # Calculate probability of Count(Sense | feature) / Count(feature)
    for sense_id in senseIDDict:
        for wordFeature in senseIDDict[sense_id]:
            numerator = senseIDDict[sense_id][wordFeature]
            denominator = unigramTable[wordFeature]
            probability = numerator / denominator
            senseIDDict[sense_id][wordFeature] = probability

            # Create a features list and add to it
            if wordFeature not in featuresDecisionList:
                featuresDecisionList.append(wordFeature)

    # Rank the list
    for feature in featuresDecisionList:

        # compare sense 1 prob with sense 2 prob
        compareProbabilities = []
        maxProbability = 0
        senseId = ""

        # getting probability value based off of feature given its sense
        for currSense_id in senseIDDict:
            currentProbability = 0

            if feature in senseIDDict[currSense_id]:
                currentProbability = senseIDDict[currSense_id][feature]

            if currentProbability > maxProbability:
                maxProbability = currentProbability
                senseId = currSense_id

            compareProbabilities.append(currentProbability)

        rankValue = None

        if compareProbabilities[0] != 0 and compareProbabilities[1] != 0:
            rankValue = abs(math.log(compareProbabilities[0] / compareProbabilities[1]))
        else:
            rankValue = abs(math.log(1))

        # Store values in decision list for ranking
        if rankValue is not None:
            rankingList[senseId + " -> " + feature] = rankValue
            senseId = ""
            maxProbability = 0

    # sort ranking list in descending order
    rankingList = dict( sorted(rankingList.items(), key=operator.itemgetter(1),reverse=True))

    # create model to print to my-model.txt
    for prediction in rankingList:
        elements = prediction.split("->")
        feature = elements[1]
        senseId = elements[0]
        rankValue = rankingList[prediction]
        senseId.strip()

        # if features are certain feature types, print to my-model.txt accordingly
        if re.search(r'^ 2L: ', feature):
            feature = re.sub(r'^ 2L: ', "", feature)
            modelFile.write("Feature: \"" + feature + "\" -2 of \"line\" -> Predicts: " + senseId + " -> Rank: " + str(rankValue) + "\n")

        elif re.search(r'^ 2R', feature):
            feature = re.sub(r'^ 2R: ', "", feature)
            modelFile.write("Feature: \"" + feature + "\" +2 of \"line\" -> Predicts: " + senseId + " -> Rank: " + str(
                rankValue) + "\n")

        elif re.search(r'^ LR', feature):
            feature = re.sub(r'^ LR: ', "", feature)
            modelFile.write("Feature: \"" + feature + "\" -1/+1 of \"line\" -> Predicts: " + senseId + " -> Rank: " + str(
                rankValue) + "\n")

        elif re.search(r'^ L', feature):
            feature = re.sub(r'^ L: ', "", feature)
            modelFile.write("Feature: \"" + feature + "\" -1 of \"line\" -> Predicts: " + senseId + " -> Rank: " + str(
                rankValue) + "\n")

        elif re.search(r'^ R', feature):
            feature = re.sub(r'^ R: ', "", feature)
            modelFile.write("Feature: \"" + feature + "\" +1 of \"line\" -> Predicts: " + senseId + " -> Rank: " + str(
                rankValue) + "\n")

        else:
            feature = re.sub(r'^ W: ', "", feature)
            modelFile.write("Feature: \"" + feature + "\" +/-2 of \"line\" -> Predicts: " + senseId + " -> Rank: " + str(
                rankValue) + "\n")

    modelFile.close()

    # Apply model created from training data to assign sense ID to test data
    for instance_id in testDict:
        testContext = testDict[instance_id]["Context"]
        testContext = Clean_Context( testContext )
        testFeatureWords = testContext.split()

        testSenseID = ""

        for testWord in testFeatureWords:
            regexp = re.compile(r'^\<head')
            testFeatureIndex = testFeatureWords.index(testWord)

            # if word is <head>line</head>
            if (regexp.search(testWord)):

                # compare each feature to element in ranking list and assign sense ID accordingly
                for element in rankingList:
                    element = element.split(" -> ")
                    senseId = element[0]
                    feature = element[1]

                    # Word To Left (-1)
                    if testFeatureIndex - 1 >= 0:
                        left_feature = "L: " + testFeatureWords[testFeatureIndex - 1]
                        if feature == left_feature:
                            testSenseID = senseId
                            # print("L Test Sense ID: ", testSenseID)
                            break

                    # Word To Right (+1)
                    if testFeatureIndex + 1 < len(testFeatureWords):
                        right_feature = "R: " + testFeatureWords[testFeatureIndex - 1]
                        if feature == right_feature:
                            testSenseID = senseId
                            # print("R Test Sense ID: ", testSenseID)
                            break

                    # -2 Words To Left
                    if testFeatureIndex - 2 >= 0:
                        two_left_features = "2L: " + " ".join(testFeatureWords[testFeatureIndex - 2:testFeatureIndex])
                        if feature == two_left_features:
                            testSenseID = senseId
                            # print("2L  Sense ID: ", testSenseID)
                            break

                    # +2 Words To Right
                    if testFeatureIndex + 2 < len(testFeatureWords):
                        two_right_features = "2R: " + " ".join(
                            testFeatureWords[testFeatureIndex + 1:testFeatureIndex + 3])
                        if feature == two_right_features:
                            testSenseID = senseId
                            # print("2R Test Sense ID: ", testSenseID)
                            break

                    # -1 and +1 Surrounding Target Term
                    if testFeatureIndex - 1 >= 0 and testFeatureIndex + 1 < len(testFeatureWords):
                        left_and_right_features = " ".join(testFeatureWords[testFeatureIndex + 1:testFeatureIndex + 3])
                        if feature == left_and_right_features:
                            testSenseID = senseId
                            # print("LR Test Sense ID: ", testSenseID)
                            break

                    # k Window size
                    if re.search(r'W:', feature):
                        # Calculate index of surrounding terms given k Window Size
                        beginningIndex = testFeatureIndex - kWindowSize
                        stopIndex = testFeatureIndex + kWindowSize

                        if beginningIndex < 0:
                            beginningIndex = 0
                        if stopIndex > len(testFeatureWords):
                            stopIndex = len(testFeatureWords)

                        testWindowFeatures = slice(beginningIndex, stopIndex + 1, 1)

                        # Store counts in dictionaries given k Window
                        for testWindowFeature in testFeatureWords[testWindowFeatures]:
                            if not re.search(r'\<head', testWindowFeature):
                                testWindowFeature = "W: " + testWindowFeature

                                if (feature == testWindowFeature):
                                    testSenseID = senseId
                                    # print( "Window Test Sense ID: ", testSenseID )
                                    break

            # assign test sense Id the most frequent ID if it is not assigned
            if testSenseID == "":
                testSenseID = higherSenseMSFB

            # assign sense id to instance id
            testDict[instance_id]["Sense_ID"] = testSenseID
        print("<answer instance=\"" + instance_id + "\" senseid=\"" + testSenseID + "\"/>")


# call main method
if __name__ == "__main__":
    main()