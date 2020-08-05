# ----------------------------------------------------------------------------------------------------------------------
# Author:         Divya Shrivastava
# Date:           01/26/2020
# Class:          CMSC 416 NLP
# File:           Eliza.py
# Function:       The purpose of this program is to be able to have conversation with the
#                 user. The program must incorporate "word spotting", in which sentences
#                 and questions can be formed using certain key words. The user talks to
#                 Eliza, a psychotherapist, who then turns those statements into questions.
#                 The following is an example program input and output:
#                 Eliza: Hello, my name is Eliza. What is your name?
#                 User: My name is Divya
#                 Eliza: Hello, Divya! How do you feel today?
#                 Divya: I am happy.
#                 Eliza: Why are you happy?
#                 Divya: I have lots of friends.
#                 Eliza: Why do you think you have lots of friends?
#                 Divya: I am not lonely
#                 Eliza: Why are you not lonely, Divya?
#                 Divya:
#                 Eliza: I'm sorry, I do not quite understand that.
#                 Divya: bye
#                 Eliza: Goodbye. Thank you for talking to me! Let's chat again soon. :)
#                 The user must compile the program, then communicate with the bot, Eliza, for as long
#                 as they would like. User must respond in full sentences. If bot asks, "How do you feel today?",
#                 user must respond saying, "I feel..." If user wishes to end the conversation, they must write "bye"
#                 The algorithm I have used to solve this issue is I have created a while loop in which the
#                 conversation does not end unless the user outputs "bye." If the user does not output "bye", the
#                 user's response is then checked against my dictionary to see if there is a match. If so, Eliza
#                 will give an associated response. If not, Eliza will ask the user to elaborate. Regex was used to
#                 parse through some specific phrases with key words to deliver a certain response using re.search
#                 and re.sub. Throughout this program, I have decided to word spot mainly for verbs describing the
#                 user themselves. This way, Eliza can respond with thought-provoking questions as to why the user
#                 does, feels, thinks, etc... As a result, the user can gain insight on themselves.
# ----------------------------------------------------------------------------------------------------------------------
import re
import random

# two-element list (dictionary) in which user responds, and eliza fetches from list for appropriate response
wordSpots = (

    # introductions, if user says anything during message to greet eliza, then respond with greetings
    ("hello", ("Hello!", "Hi!")),
    ("hi", ("Hi!", "Hello!")),
    ("how are you", "I'm fine, thank you. How is your day?"),

    # talking about user themselves... word spotting verbs about user to ask for explanations or to think about why they feel that way
    ("i think (.*)", "Do you really think so?"),
    ("i feel (.*)", "Tell me more about these feelings."),
    ("i don't (.*)", ("Why don't you {}?", "Do you want to {}?")),
    ("i don't know (.*)", "Maybe you can do some research and find out."),
    ("my (.*)",  ("Why do you say that?", "What makes you reach that conclusion?")),
    ("i crave (.*)", "Tell me more about your cravings."),

    # questions for eliza --> if eliza is asked about herself, she will redirect conversation back to user
    ("are you (.*)", "Let us talk about you, not me. Are you okay?"),
    ("you are (.*)", ("Do you mean yourself in this case?")),
    ("you (.*)", "This conversation is about you, not me. How are you feeling?"),

    # questions in general --> user needs to think or expand on what they said
    ("why (.*)", "What do you think?"),
    ("is there (.*)", ("Do you think there is?", "Would you like there to be?")),

    # single responses that require more explanation
    ("yes", "Tell me more."),
    ("no", "Why not?"),

    # verbs in middle of sentence
    ("(.*) is (.*)", "Why is {} {}?"),
    ("(.*) are (.*)", "Why are {} {}?"),
    ("(.*) can't (.*)", "Why can't {} {}?"),

    # unclear as to what the user said
    ("i (.*)", "Why is that so?"),
    ("(.*)", ("Can you please elaborate?", "Tell me more.", "I'm sorry, I do not quite understand that. Can you explain further?")),
)

# Beginning of program - introductions between Eliza and user
print("Hello, my name is Eliza. What is your name? (When you want to end the session, type 'bye')")
name = input()

# if user does not input anything, user is prompted to write a name
if name == "":
    print("I'm sorry, I did not understand that. What is your name?")
    name = input()

# eliza responds once name is presented
print("Hello, " + name + "! How do you feel today?")

flag = True

# while loop so that eliza continuously responds until user states otherwise
while flag:

    # every time it is user's time to respond, there will be "> " to indicate their turn
    userResponse = input( "> " ).replace( ",", "" )
    words = userResponse.split()
    answer = ' '

    # if user says bye, then terminate program
    if userResponse == "bye":
        print("Goodbye. Thank you for talking to me! Let's chat again soon. :)")
        flag = False

    # else parse through user's statement to respond
    else:
        userResponse.lower()

        # search for phrases within the wordSpots dictionary
        for phrases in wordSpots:

            # if user states "I need..." eliza transforms into "Why do you need...?"
            if re.search(r'^I|i', userResponse) and re.search('^(.*?)\s(need)\s(.*?)$', userResponse):
                tokens = re.search('^(.*?)\s(need)\s(.*?)$', userResponse)
                beginning = tokens.group(1)
                middle = tokens.group(2)
                end = tokens.group(3)
                end = end + "?"
                print(re.sub(r'^I|i', name + ", why do you think you", beginning), middle, end)
                break

            # if user states "I am..." eliza transforms into "Why are you...?"
            elif re.search(r"^I|i\s(.*?)$", userResponse) and re.search('^(.*?)\s(am)\s(.*?)$', userResponse):
                tokens = re.search(r'^(.*?)\s(am)\s(.*?)$', userResponse)
                beginning = tokens.group(1)
                middle = tokens.group(2)
                end = tokens.group(3)
                end = end + ", " + name + "?"
                print(re.sub(r"^I|i", "Why are you", beginning), end)
                break

            # if user states "I have..." eliza transforms into "Why do you think you have...?"
            elif re.search(r'^I|i', userResponse) and re.search('^(.*?)\s(have)\s(.*?)$', userResponse):
                tokens = re.search('^(.*?)\s(have)\s(.*?)$', userResponse)
                beginning = tokens.group(1)
                middle = tokens.group(2)
                end = tokens.group(3)
                end = end + "?"
                print(re.sub(r'^I|i', "Why do you think you", beginning), middle, end)
                break

            # if user states "I cannot..." eliza transforms into "Why can't you...?"
            elif re.search(r"^I|i\s(.*?)$", userResponse) and re.search('^(.*?)\s(cannot)\s(.*?)$', userResponse):
                tokens = re.search(r'^(.*?)\s(cannot)\s(.*?)$', userResponse)
                beginning = tokens.group(1)
                middle = tokens.group(2)
                end = tokens.group(3)
                end = end + "?"
                print(re.sub(r"^I|i", name + ", why can't you", beginning), end)
                break

            # if user states "I like..." eliza transforms into "Why do you like...?"
            elif re.search(r"^I|i\s(.*?)$", userResponse) and re.search('^(.*?)\s(like)\s(.*?)$', userResponse):
                tokens = re.search(r'^(.*?)\s(like)\s(.*?)$', userResponse)
                beginning = tokens.group(1)
                middle = tokens.group(2)
                end = tokens.group(3)
                end = end + "?"
                print(re.sub(r"^I|i", name + ", why do you", beginning), middle, end)
                break

            # if user states "I hate..." eliza transforms into "Why do you hate...?"
            elif re.search(r"^I|i\s(.*?)$", userResponse) and re.search('^(.*?)\s(hate)\s(.*?)$', userResponse):
                tokens = re.search(r'^(.*?)\s(hate)\s(.*?)$', userResponse)
                beginning = tokens.group(1)
                middle = tokens.group(2)
                end = tokens.group(3)
                end = end + "?"
                print(re.sub(r"^I|i", name + ", why do you", beginning), middle, end)
                break

            # if user states "{a} are {b}..." eliza transforms into "Why are {a} {b}?"
            elif re.search('^(.*?)\s(are)\s(.*?)$', userResponse):
                tokens = re.search(r'^(.*?)\s(are)\s(.*?)$', userResponse)
                beginning = tokens.group(2)
                middle = tokens.group(1)
                end = tokens.group(3)
                end = end + "?"
                print(re.sub(r'^(.*?)\s(are)\s(.*?)$', name + ", why are", beginning), middle, end)
                break

            # if user states "I want..." eliza transforms into "Why do you want...?"
            elif re.search(r'^I|i', userResponse) and re.search('^(.*?)\s(want)\s(.*?)$', userResponse):
                tokens = re.search('^(.*?)\s(want)\s(.*?)$', userResponse)
                beginning = tokens.group(1)
                middle = tokens.group(2)
                end = tokens.group(3)
                end = end + ", " + name + "?"
                print(re.sub(r'^I|i', "Why do you", beginning), middle, end)
                break

            # else if user's response matches any of the phrases in wordSpots dictionary that was NOT listed above, find associated responses
            elif re.match(phrases[0], userResponse):
                elementsOfTuple = phrases[1]

                # if there is a tuple of appropriate responses (more than 1), randomize answer
                if isinstance(elementsOfTuple, tuple):
                    userResponse = random.choice(elementsOfTuple)

                # else get answer (since there is only one)
                else:
                    userResponse = elementsOfTuple

                # display Eliza's response to user's statement
                answer = userResponse + ' '
                print(answer)
                break

    userResponse = ""
