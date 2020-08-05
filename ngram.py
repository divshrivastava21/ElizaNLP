# ----------------------------------------------------------------------------------------------------------------------
# Author:         Divya Shrivastava
# Date:           02/12/2020
# Class:          CMSC 416 NLP
# File:           ngram.py
# Function:       The purpose of this program is to create a Python program that will learn an N-gram language
#                 model from a random number of plain text files. Furthermore, the program should generate a
#                 random number of sentences based on the number input by the user. How the N-gram language model
#                 should work is that based on the value of n, the program should be able to generate a sequence of n
#                 items. The higher the value of n, the more coherent the randomly generated sentence (based off of
#                 probability) should be.
#                 The following is an example program input and output:
#                 command line prompt: ngram.py 1 4 WarAndPeace.txt
#                 output: every enter now severally so, let you. die he breath on tomb me.i dog feast cat now. a more
#                 to leg less now you enter.
#                 The user must compile the program and input three arguments - the n value for n-grams, number of
#                 sentences they want generated, and the corpus (text) from which the sentences are observed from.
#                 After, the program reads in the file and based off of the value of n, it determines if a dictionary
#                 for the history (or past words) must be used. If the value of n is 1, then an array for a unigram is
#                 created in which the probability of each word is calculated and compared to a random number in order
#                 to output random words in a sentence. The other algorithm I utilized is if the n value is 2 or
#                 greater. If n is greater than or equal to 2, two dictionaries are created. One to store the key
#                 (each token) and value (the frequency of each token). The other one is to keep track of the history
#                 of each word (counter). If n is equivalent to 1, then counts of each word used is stored into one
#                 array. Two methods were created to generate random sentences. One for 2+-grams and one for unigrams.
#                 The 2+-gram function parses through both the outer and inner dictionary and determines the probability
#                 of the word following the previous word to determine what word follows in the generated sentence.
#                 For the unigram function, the frequency and probability of each word in the unigram table was
#                 calculated and compared with a random probability number to determine the randomly generated
#                 sentence as well. Although this function performs the same function, it is different because it does
#                 not need an inner dictionary for history for comparison.
# -----------------------------------------------------------------------------------------------------------------------
import sys
import re
import random

# generate Sentences for 2 or more gram models
def generateSentences(numberOfGrams, numberOfSentences, diction, hdict):

    # print out as many sentences as user wants
    for i in range(numberOfSentences):
        wordPopulation = []

        # add n - 1 gram start tags!
        for j in range(numberOfGrams - 1):
            wordPopulation.append("<s>")
        currSentence = ""

        # while newly generated sentence does not contain end tag
        while "<end>" not in wordPopulation:

            # add word to history
            history = ' '.join(wordPopulation)

            # determine value (or count) of history in outer dictionary
            nested_numerator = diction[history]

            # denominator is total number of tokens that follow the given history
            denominator = hdict[history]
            sum = 0

            # for each word in the dictionary given the history
            for word in nested_numerator:

                # probability is counts of token / total counts of words following history
                probability = nested_numerator[word] / denominator  # 0.3 0.4 0.3
                randomNum = random.uniform(0, 1)  # 0.6
                sum += probability

                if (randomNum <= sum):

                    # if word is the end tag, then add it to the current sentence and append the array
                    if word == "<end>":
                        currSentence += " ".join(wordPopulation) + " " + word
                        wordPopulation.pop(0)
                        wordPopulation.append(word)
                    # else simply add removed word from beginning of array and add word to array
                    else:
                        currSentence += wordPopulation.pop(0) + " "
                        wordPopulation.append(word)
                    break
        # remove all start and end tags and empty spaces.
        currSentence = re.sub(r'<s>', "", currSentence)
        currSentence = re.sub(r'<end>', "", currSentence)
        currSentence = re.sub(r'^\s+|\s+$', "", currSentence)
        print(str(i + 1) + ": " + currSentence + ".")

# generate sentences for unigrams only
def generateUniGramSentences(numberOfSentences, totalUniGramSum, unigramTable):

    # generate as many sentences as user wants
    for i in range(numberOfSentences):
        currSentence = ""
        probabilitySum = 0

        # while the end tag is not in the currently generated sentence
        while "<end>" not in currSentence:

            #set random number value
            randomNum = random.uniform(0, 1)

            # parse through each token in the unigram table
            for token in unigramTable:

                # calculate probability of token count given total unigram table count and add to the sum
                probability = unigramTable[token] / totalUniGramSum
                probabilitySum += probability

                # if the random num is <= probability sum, then add token to the sentence and set sum back to 0
                if randomNum <= probabilitySum:
                    currSentence += token + " "
                    probabilitySum = 0
                    break

        #remove end tags and white spaces
        currSentence = re.sub(r'<end>', "", currSentence)
        currSentence = re.sub(r'^\s+|\s+$', "", currSentence)
        print(str(i + 1) + ": " + currSentence + ".")


def main():
    # second argument is 'n', third is number of randomly generated sentences
    numberOfGrams = int(sys.argv[1])
    numberOfSentences = int(sys.argv[2])

    print("This program generates random sentences based on an N-gram model (" + str(numberOfGrams) + "-gram model). "
        "The number of sentences needed to be generated are " + str(numberOfSentences) + ". The  author is Divya Shrivastava.")

    # if user does not input n gram value of 1 or greater, exit program
    if (numberOfGrams < 1):
        print("n must be greater than or equal to 1.")
        exit()

    # ngrams array
    ngram = []

    # dictionary hash table
    diction = {}
    hdict = {}
    unigramTable = {}

    totalUniGramSum = 0
    fileIndex = 3

    # run all files
    while fileIndex < len(sys.argv):

        #retrieve, open, read file and replace new line character with empty space
        file = sys.argv[fileIndex]
        inputFile = open(file, encoding="utf8")
        readFile = inputFile.read()
        readFile = re.sub('\n', " ", readFile)

        # split file into sentences and store in array
        sentences = readFile.split(".")

        # for each element in the sentences array
        for i in range(len(sentences)):

            # set currentSequence to index i in sentences array
            currSentence = sentences[i]

            # if there length is null, break out of loop
            if len(currSentence) < 1:
                break

            history = ""

            # set history to ngrams - 1 tag "<s>"
            for i in range(numberOfGrams - 1):
                history += "<s> "

            # remove all quotes and punctuation from sentence
            currSentence = re.sub(r'[^a-zA-Z0-9\s]', "", currSentence)

            # add start and end tags to newly edited sentence & split sentence into tokens
            currSentence = history + currSentence + " <end>"
            tokens = currSentence.split()

            # if length of tokens is less than ngrams, break out of loop
            if (len(tokens) < numberOfGrams):
                break

            # if ngrams is 2 or greater
            if numberOfGrams >= 2:

                # parse through each token in sentence
                for i in range(len(tokens)):

                    # add token to ngram array
                    ngram.append(tokens[i])

                    # if ngram array length is equal to ngrams
                    if len(ngram) == numberOfGrams:

                        # word is equivalent to removed token from ngram array and added on to history
                        word = ngram.pop()
                        history = ' '.join(ngram)

                        # create hash if not in table already
                        if history not in diction:
                            diction[history] = {}
                            hdict[history] = 0

                        # create hash if not in table already
                        if word not in diction[history]:
                            diction[history][word] = {}
                            diction[history][word] = 0

                        # increment hash table for that specific word by 1 in dictionary, and increment hdict by 1
                        diction[history][word] += 1
                        hdict[history] += 1

                        # add word to ngram array and shift elements by removing first element in list
                        ngram.append(word)
                        ngram.pop(0)

                    # break out of loop if end of sentence has reached
                    if tokens[i] == "<end>":
                        break
            # if it is a unigram
            else:
                # for each token in sentence
                for token in tokens:
                    totalUniGramSum += 1
                    # if token is already in unigramTable, increment by 1
                    if token in unigramTable:
                        unigramTable[token] += 1
                    # else set value to 1
                    else:
                        unigramTable[token] = 1
        # close file
        inputFile.close()
        fileIndex += 1

    # parse through dictionaries to calculate probabilities and construct sentences if ngram is 2 or more
    if (numberOfGrams >= 2):
        generateSentences(numberOfGrams, numberOfSentences, diction, hdict)

    # else parse through unigramTable
    else:
        generateUniGramSentences(numberOfSentences, totalUniGramSum, unigramTable)


# call main method
if __name__ == "__main__":
    main()
