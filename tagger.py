# ----------------------------------------------------------------------------------------------------------------------
# Author:         Divya Shrivastava
# Date:           03/05/2020
# Class:          CMSC 416 NLP
# File:           tagger.py
# Function:       The purpose of this program is to create a Python program that will take as input a training file
#                 containing part of speech (POS) tagged text and a file containing text that needs to be POS tagged. In
#                 order to execute this program, a greedy tagger must be created that is based on the probability of the
#                 tag given the word (or vice versa) and the probability of the previous tag. After analyzing the
#                 training data, this program should take each word in the test data and assign the POS tag that
#                 maximizes the P(w|t)*P(tag|prevTag). If a word is not assigned a tag in the training data,
#                 automatically assign the tag "NN" to that word. The accuracy of the most likely tagger on a given
#                 test file is 85.14%.
#
#                 The following is an example program input and output:
#                 command line prompt: tagger.py pos-train.txt pos-test.txt > pos-test-with-tags.txt
#                 output: a file containing text that had been part-of-speech tagged.
#
#                 The user must compile the program and input three arguments - the file that contains text that is
#                 already part-of-speech  tagged, the file that contains text that needs to be tagged, and the file to
#                 which the part-of-speech tagged text will eventually be output to. For this program, I started off by
#                 reading in the training data first and parsing through it. I separated each word-tag set into an array
#                 as each token. Then, I split the word and tag into individual tokens (through a for loop) in order to
#                 store the counts into four separate dictionaries. Two dictionaries were nested - one for the
#                 dict[word][tag] and one for the tagDict[previousTag][tag]. I also created two regular dictionaries -
#                 one for the wordDict[word] itself and one for the prevTagDict[previousTag]. Once the models in these
#                 dictionaries were created after parsing through the entire training data, then another function was
#                 called in order to read the test data, parse through it, and assign part-of-speech tags. If the tag
#                 in the test data was not a tag already seen in the training data given a previous tag, then la place
#                 smoothing was utilized to determine what the following tag would be. The maximum probability for the
#                 most likely tagger was calculated by multiplying the two probabilities as stated earlier. As each tag
#                 was assigned to a word, it was printed out to the file.
# -----------------------------------------------------------------------------------------------------------------------

import re
import sys

# function to tag words with highest probability of a certain part of speech tag
def partOfSpeechTagger(openedFile, diction, wordDict, tagDict, prevTagDict):
    # read in and parse through to-be-tagged text file
    openedFile = re.sub('\[', " ", openedFile)
    openedFile = re.sub('\]', " ", openedFile)
    openedFile = re.sub('\n', " ", openedFile)

    sentences = openedFile.split("\b\.\b")
    maxProbability = 0
    currMaxTag = ""

    # read through each sentence in array
    for i in range(len(sentences)):
        currSentence = sentences[i]
        currSentence = re.sub('^\s+', "", currSentence)

        # if there length is null, break out of loop
        if len(currSentence) < 1:
            continue

        # split words into individual tokens
        wordList = currSentence.split()

        # HOW TO IMPLEMENT PREVIOUS TAG INTO PROBABILITY
        previousTag = "<s>"

        # while the sentence is not over, parse through the dictionaries for the probability of the word
        # given that tag and the probability of tag given previous tag
        for word in wordList:

            # account for words not in train text but in test
            if word not in wordDict:
                tag = "NN"
                print(word + "/" + tag)
            else:
                wordNumerator = diction[word]
                wordDenominator = wordDict[word]


                # parse through each tag associated with word
                for tag in wordNumerator:


                    # If tag was not in the tagDict given a previous tag
                    if tag not in tagDict[previousTag]:
                        smoothing = 1 / (len(tagDict) + len(prevTagDict))
                        currProbabilityWordTag = wordNumerator[tag]/wordDenominator
                        currTotalProbability = smoothing*currProbabilityWordTag

                        if maxProbability < currTotalProbability:
                            maxProbability = currTotalProbability
                            currMaxTag = tag
                    else:
                        prevTagNumerator = tagDict[previousTag][tag] + 1
                        prevTagDenominator = prevTagDict[previousTag] + len(prevTagDict)

                        #calculate probability of tag given previous tag
                        currProbabilityTagTag = prevTagNumerator/prevTagDenominator

                        # calculate probability of word given tag
                        currProbabilityWordTag = wordNumerator[tag]/wordDenominator

                        # calculate total probability by multiplying previous two probabilities
                        currTotalProbability = currProbabilityWordTag*currProbabilityTagTag

                        # pick the tag with the highest probability and assign it to the word
                        if maxProbability < currTotalProbability:
                            maxProbability = currTotalProbability
                            currMaxTag = tag
                # assign tag to previous tag for next word
                previousTag = currMaxTag

                print(word + "/" + currMaxTag)
                maxProbability = 0
                currMaxTag = ""

def main():

    taggedText = sys.argv[1]
    willBeTaggedText = sys.argv[2]

    openPosTrainText = open(taggedText, encoding="utf8")
    readPosTrainText = openPosTrainText.read()

    readPosTrainText = re.sub('\[', " ", readPosTrainText)
    readPosTrainText = re.sub('\]', " ", readPosTrainText)
    readPosTrainText = re. sub('\n', " ", readPosTrainText)
    sentences = readPosTrainText.split("./.")

    # dictionary hash table
    diction = {}
    wordDict = {}

    prevTagDict = {}
    tagDict = {}


    openPosText = open(willBeTaggedText, encoding="utf8")

    for i in range(len(sentences)):
        currSentence = sentences[i]
        currSentence = re.sub('^\s+', "", currSentence)

        # if the length is null, break out of loop
        if len(currSentence) < 1:
            break

        currSentence = "<s> " + currSentence + " ./."
        wordTagPairs = currSentence.split()

        prevTag = ""
        for wordTagPair in wordTagPairs:
            if re.search(r"/", wordTagPair):
                wordTagSep = wordTagPair.split("/")
                if len(wordTagSep) >= 2:

                    word = wordTagSep[0]
                    tag = wordTagSep[1]

                    # create hash if not in table already
                    if word not in diction:
                        diction[word] = {}
                        wordDict[word] = 0

                    if prevTag not in tagDict:
                        tagDict[prevTag] = {}
                        prevTagDict[prevTag] = 0

                    if tag not in tagDict[prevTag]:
                        tagDict[prevTag][tag] = {}
                        tagDict[prevTag][tag] = 0

                    # create hash if not in table already
                    if tag not in diction[word]:
                        diction[word][tag] = {}
                        diction[word][tag] = 0

                    # increment hash table for that specific word by 1 in dictionary, and increment wordDict by 1
                    diction[word][tag] += 1
                    wordDict[word] += 1
                    tagDict[prevTag][tag] += 1
                    prevTagDict[prevTag] += 1

                    # resetting previous tag
                    prevTag = tag
            else:
                prevTag = "<s>"
    openPosText = open(willBeTaggedText, encoding="utf8")
    readPosText = openPosText.read()

    partOfSpeechTagger(readPosText, diction, wordDict, tagDict, prevTagDict)

# call main method
if __name__ == "__main__":
    main()