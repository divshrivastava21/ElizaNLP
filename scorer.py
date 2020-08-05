# ----------------------------------------------------------------------------------------------------------------------
# Author:         Divya Shrivastava
# Date:           03/29/2020
# Class:          CMSC 416 NLP
# File:           scorer.py
# Function:       The purpose of this program is to create a Python program that will compare the tagged sense text
#                 output created from wsd.py to the golden key standard file already created. If the senses displayed
#                 in the sensed text for each word matches the sense ID's displayed in the golden key for each word,
#                 then the counter is incremented by 1 and it is marked as "correct." Additionally, this program also
#                 displays the accuracy by comparing the correct counts by the total counts.
#
#                 The following is an example program input and output:
#                 command line prompt: scorer.py my-line-answers.txt line-key.txt
#                 output: a confusion matrix with the accuracy score displayed as well
#                 Accuracy: 0.8425
#                          phone   product
#                 phone     55       17
#                 product    3       51
#
#                 The user must compile the program and input two arguments - the test file with sense IDs and the gold
#                 key with sense ID's. After, the program reads in both the test file and gold key to compare how
#                 accurate the wsd.py program was in assigning sense ID's. In order to do this, the elements in the
#                 gold key standard and the test file are compared line by line. Then, the sense IDs are pulled out
#                 from each array in order to create the confusion matrix. A nested dictionary is created to be able to
#                 retrieve all the predicted sense IDs with each golden key sense IDs (outer dictionary). Then, to call
#                 the predicted sense ID counts for each gold key Sense ID, a for loop within a for loop was written to
#                 obtain the values. Finally, the accuracy and confusion matrix were output into the file. The accuracy
#                 of the tagging assignments was 84.25%.
# -----------------------------------------------------------------------------------------------------------------------

import re
import sys

def main():

    # take in tagged text and golden key from command line arguments
    taggedSenseOutput = sys.argv[1]
    goldenKey = sys.argv[2]

    correctCounter = 0
    totalCounter = 0
    diction = {}

    # parse my-line-answers text into array of lines
    taggedSenseOutputText = open(taggedSenseOutput, encoding="utf8")
    taggedSenseWords = taggedSenseOutputText.read()
    predictedSenseLine = taggedSenseWords.split('\n')

    # parse golden key into array of lines
    goldenKeyText = open(goldenKey, encoding="utf8")
    goldenWords = goldenKeyText.read()
    goldenline = goldenWords.split('\n')

    # parse through both arrays to compare and calculate accuracy
    for i in range(len(predictedSenseLine)):

        # store values in my-line-answers array as phone if sense ID is phone
        if re.search(r'phone', predictedSenseLine[i]):
            predictedSenseLine[i] = "phone"

        # store values in my-line-answers array as product if sense ID is product
        if re.search(r'product', predictedSenseLine[i]):
            predictedSenseLine[i] = "product"

        # # store values in golden key array as phone if sense ID is phone
        if re.search(r'phone', goldenline[i]):
            goldenline[i] = "phone"

        # store values in golden key array as product if sense ID is product
        if re.search(r'product', goldenline[i]):
            goldenline[i] = "product"

        # if arrays match for that line, increment counter to be able to calculate accuracy
        if(predictedSenseLine[i] == goldenline[i]):
            correctCounter += 1

        # add golden key Sense to dictionary
        if goldenline[i] != "" and goldenline[i] not in diction:
            diction[goldenline[i]] = {}

        # add predicted key sense to dictionary
        if predictedSenseLine[i] != "" and predictedSenseLine[i] not in diction[goldenline[i]]:
            diction[goldenline[i]][predictedSenseLine[i]] = {}
            diction[goldenline[i]][predictedSenseLine[i]] = 0

        # increment counter for predicted key sense for that specific golden sense key by 1
        if predictedSenseLine[i] != "" and goldenline[i] != "":
            diction[goldenline[i]][predictedSenseLine[i]] += 1

        # keep track of total number of counts
        totalCounter += 1

    # sort dictionary
    goldenSenseList = sorted(diction.keys())

    accuracy = correctCounter/totalCounter
    print("Accuracy: " + str(accuracy))
    print()

    #parse through each golden sense key within the sorted dictionary to print out all the tags
    print("      ", end="")
    for index in range(len(goldenSenseList)):
        print(goldenSenseList[index], end=" ")
    index = 0

    # parse through each golden sense key within the sorted dictionary to print out count when predicte key tag matches golden key tag
    for goldenSense in goldenSenseList:
        predictedDict = diction[goldenSense]

        print()
        print(goldenSenseList[index], end = " ")
        index += 1

        # parse through each predicted key tag within the sorted dictionary
        for predictedSenseTag in goldenSenseList:

            # if predicted key tag is not already within dictionary, then value should be 0. Else, add count for matching
            if(predictedSenseTag not in predictedDict):
                print (0, end = " ")
            else:
                print("  " + str(predictedDict[predictedSenseTag]), end = " ")

# call main method
if __name__ == "__main__":
    main()