# Author: Divya Shrivastava
# File: Assignment7.py
# Course: CMSC 403
# Date: 04/08/2020
from tkinter import *

# Class that takes in height and width of canvas and displays it
class CustomCanvas:

    # set top bar on screen
    root = Tk()
    root.title("CMSC 403 Assignment 7 by Divya Shrivastava: 04/11/2020")

    # constructor that takes in height and width of canvas
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.container = Canvas(self.root, height=self.height, width=self.width, bg="#00FF00")

    # display UI box
    def draw_screen(self):
        self.container.mainloop()

    # Creating each rectangle on the screen
    def create_rect_on_canvas(self, rect):
        self.container.create_rectangle(rect.x, rect.y, rect.x + rect.width, rect.y + rect.height, fill='green')

    # display the canvas on UI box with rectangles
    def display(self):
        self.container.pack()


# Class that creates rectangles with given dimensions
class Rectangle():

    # constructor that takes in four parameters for rectangle and presets x and y values to 0
    def __init__(self, height, width, x=0, y=0):
        self.height = height
        self.width = width
        self.x = x
        self.y = y

    # to be able to print out rectangle dimensions
    def __str__(self):
        return '{self.height}, {self.width}, {self.x}, {self.y}'.format(self=self)

# function that returns list of rectangles with newly assigned x and y values
def pack(allRect, canvasSize):

    # create function to get height of each rectangle and then sort accordingly
    def getHeight(rect):
        return rect.height
    allRect.sort(key=getHeight, reverse=True)

    # unpack tuple with canvas height and width
    canvasHeight = canvasSize[0]
    canvasWidth = canvasSize[1]

    # boolean to keep track of rectangles staying within canvas size
    withinCanvas = False

    # pre-set the first rectangle height as a value
    currVal = 0
    checkVal = allRect[0].height

    # parse through each rectangle to assign it x and y values
    for rectangle in allRect:

        # as long as the index of each element is past 0, then assign x and y values of rectangle
        if(allRect.index(rectangle) > 0):
            rectangle.x = (allRect[allRect.index(rectangle) - 1].x + allRect[allRect.index(rectangle) - 1].width)
            rectangle.y = currVal

            # check to see if rectangle is within canvas width; if not, reassign x and y values
            if((rectangle.x + rectangle.width) > int(canvasWidth)):
                withinCanvas = True
                rectangle.x = 0
                currVal = checkVal
                rectangle.y = currVal


            # as long as rectangle is within canvas, can reassign y value to check with other rectangles
            if(withinCanvas):
                withinCanvas = False
                checkVal = rectangle.y + rectangle.height
    return allRect


# main function to read in file and display canvas with rectangle
def main():
    global canvas

    # open file, read and parse it.
    file_path = sys.argv[1]
    openFile = open(file_path, encoding="utf-8")
    openFile = openFile.readlines()
    rectangleList = []
    canvasTuple = []

    # to analyze and store each line in file
    for line in range(len(openFile)):

        openFile[line] = re.sub(r'\n','', openFile[line])
        splitLine = openFile[line].split(",")

        if line == 0:
            canvasHeight = int(splitLine[0])
            canvasWidth = int(splitLine[1].rstrip())
            canvas = CustomCanvas(canvasHeight, canvasWidth)
            canvasTuple = [str(canvasHeight), str(canvasWidth)] # tuple to use in pack function
        else:
            rectangle = Rectangle(int(splitLine[0]), int(splitLine[1]), 0, 0) # create each Rectangle object
            rectangleList.append(rectangle) # add each Rectangle object to the list

    # pack function returns a list with rectangles and their x- and y- coordinates
    returnedRectangleList = pack(rectangleList, canvasTuple)

    # create the rectangle on the canvas
    for rectangle in returnedRectangleList:
        canvas.create_rect_on_canvas(rectangle)

    # display canvas and the rectangles on it
    canvas.display()
    canvas.draw_screen()

if __name__ == '__main__':
    main()