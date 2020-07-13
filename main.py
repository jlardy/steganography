from tkinter import filedialog
from tkinter import *
import numpy as np
import random
import os
from utils import *
from PIL import Image 

# initialize tkinter root and a string var to represent the loading bar for the gui
root = Tk()
loadingBar = StringVar()

###################################################################################################################################
# Image in image section begins here

def bruteForceOptimizer(desiredSize, length, width):
    # poorly written function, really inefficent but i couldnt think of a better way to do it. 
    # Finds the optimal dimensions of a sub-image if its too big for the outer image
    ratio = 0.01
    previous = 0
    while True:
        if ((length * ratio) * (width * ratio) * 8) + len(binaryFileSize(round(length * ratio))) + len(binaryFileSize(round(width * ratio))) > desiredSize:
            break
        else:
            previous = ratio
            ratio += .01
    return previous

def imgInImg(img1, img2, outputFileName='out.png'):
    # img2 is stored in img1 
    img1 = np.array(Image.open(img1))
    img2 = np.array(Image.open(img2))

    # the dimensions of the image to be hidden
    length = binaryFileSize(img2.shape[0])
    width = binaryFileSize(img2.shape[1])

    if (img2[:,:,0].size * 8) + len(length) + len(width) > img1[:,:,0].size*2:
        answer = query_yes_no('Whoops the image is too large to input, would you like to resize it?')
        
        if answer:
            ratio = bruteForceOptimizer(img1[:,:,0].size * 2, img2.shape[0], img2.shape[1])

            newLength = round(getFileInt(length) * ratio)
            newWidth = round(getFileInt(width) * ratio)
            
            length = binaryFileSize(newLength)
            width = binaryFileSize(newWidth)
            img2 = np.array(Image.fromarray(img2).resize((newWidth, newLength)))
        else:
            return  
    
    # use PIL to optimize the file sizes before embedding them
    img1 = Image.fromarray(img1)
    img1.save('temp.png', optimized=True, quality=95)
    img1 = np.array(Image.open('temp.png'))

    # preprends the image demsions to each band string
    redStr = length + width
    greenStr = length + width
    blueStr = length + width
    
    # create the binary strings for each color band
    for row in img2:
        for column in row:
            redStr += int2bin(column[0])
            greenStr += int2bin(column[1])
            blueStr += int2bin(column[2])
      
    index = 0
    stop = False
    # loop through the image and insert two bits of img2's pixels into img1
    for row in img1:
        if stop:
            break
        for column in row:
            if index > len(redStr)-1:
                stop = True
                break
            column[0] = insertTwoBits(column[0], redStr, index)
            column[1] = insertTwoBits(column[1], greenStr, index)
            column[2] = insertTwoBits(column[2], blueStr, index)
            updateVariable(index, len(redStr))
            index += 2
    
    updateVariable(0, 0)        
    new = Image.fromarray(img1)
    new.save(outputFileName)
    os.remove("temp.png")

def getImgFromImg(img, outputFileName='foundImage.png'):
    # get the image
    data = np.array(Image.open(img))

    rStr = ''
    gStr = ''
    bStr = ''
    length = ''
    width = ''

    stop = False 
    foundLength = False
    foundWidth = False
    calculatedItems = False

    counter = 0
    size = 0
    # Loop through the encoded image, first gets the length and width of the hidden image then gets the image data itself
    for row in data:
        if stop:
            break
        for column in row:
            if not foundLength:
                length += int2bin(column[0])[-2:]
                if not len(length)%8 and length[-8:] == int2bin(0):
                    foundLength=True
                    length = getFileInt(length)

            elif not foundWidth:
                width += int2bin(column[0])[-2:]
                if not len(width)%8 and width[-8:] == int2bin(0):
                    foundWidth=True
                    width = getFileInt(width)

            else:
                if foundLength and foundWidth and not calculatedItems:
                    # calculate the number of pixels that will be found 
                    size = length * width * 8
                    calculatedItems = True
                rStr += int2bin(column[0])[-2:]
                gStr += int2bin(column[1])[-2:]
                bStr += int2bin(column[2])[-2:]
                updateVariable(len(rStr), size)
                if len(rStr) == size:
                    stop = True
                    break
    
    # build the image from lists of ints converted from the binary strings by calling intArray function 
    out = np.stack((intArrayFromBin(rStr),intArrayFromBin(gStr),intArrayFromBin(bStr)),axis=1)
    out = np.reshape(out, (length, width, 3))
    # convert form an aray to image and save
    new = Image.fromarray(out.astype('uint8'))
    new.save(outputFileName)
    updateVariable(0,0)


###################################################################################################################################
# Text insertion begins here

# encodes a file, currently only works by exporting the image as a PNG
def encode(inputFile, inString, outputFileName='out.png', twoBits=True, stringInput=True):
    complete = False

    if not stringInput:
        with open(inString, 'r') as txtfile:
            inString = txtfile.read()
    
    if twoBits:
        numBits = 2
    else:
        numBits = 1

    index = 0
    tmp = Image.open(inputFile)
    tmp.save('temp.png', optimized=True, quality=95)
    # read image data into numpy array
    data = np.array(Image.open('temp.png'))
    # convert the input string to binary 
    binString = str2bin(inString)
    # prepend the length to the binary 
    binString = binaryFileSize(len(binString)) + binString

    if twoBits:
        if len(binString) >= (data.size)*2:
            print('Input is too long to be hidden within the image. ')
            return 
    else:
        if len(binString) >= data.size:
            print('Input is too long to be hidden within the image. ')
            return 
    # loop through the numpy array and insert binary data 
    for row in data:
        if complete:
            break
        for column in row:
            if complete:
                break
            for i in range(len(column)):
                if index > len(binString)-1: 
                    complete = True
                    break
                if twoBits:
                    column[i] = insertTwoBits(column[i], binString, index)
                else:
                    column[i] = insertBit(column[i], binString, index)
                index += numBits
                updateVariable(index, len(binString))
    
    updateVariable(0,0)
    new = Image.fromarray(data)
    new.save(outputFileName)
    os.remove("temp.png")

# decodes an input file that has been previously encoded 
def decode(inputFile, twoBits=True):
    numBits = 2 if twoBits else 1
    out = ''
    size = ''
    stop = False
    text = False
    foundSize = False
    # get the image
    data = np.array(Image.open(inputFile))
    # loop through and build a binary string from the lsb until the delimeter is included in the string 
    for row in data:
        if stop:
            break
        for column in row:
            if stop:
                break
            for i in range(len(column)):
                if not foundSize:
                    size += int2bin(column[i])[-numBits:]
                    if not len(size)%8 and size[-8:] == int2bin(0):
                        foundSize=True
                        size = getFileInt(size)
                else:
                    out += int2bin(column[i])[-numBits:]
                    updateVariable(len(out), size)
                    if len(out) == size:
                        stop = True
                        text=True
                        break
    if text:
        updateVariable(0,0)
        return bin2txt(out)
    else:
        return 'No text found.'

def createSet(imgArr, binMessageLength, occupied):
    positions = set()
    length, width, dimensions = imgArr.shape
    random.seed(length)

    while len(positions) != binMessageLength:
        newPos = (random.randint(0,length-1), random.randint(0,width-1), random.randint(0,dimensions-1))
        if newPos not in occupied:
            positions.add(newPos)
    return positions

def insertRandomly(inputFile, inString, outputFileName='out.png', twoBits=True, stringInput=True):
    # set stringInput to false if you are passing a file path 
    if not stringInput:
        with open(inString, 'r') as txtfile:
            inString = txtfile.read()

    complete = False
    numbits = 2 if twoBits else 1
    index = 0
    tmp = Image.open(inputFile)
    tmp.save('temp.png', optimized=True, quality=95)

    # read image data into numpy array
    data = np.array(Image.open('temp.png'))
    # convert the input string to binary 
    binString = str2bin(inString)

    fileSize = binaryFileSize(len(binString))
    if len(binString)+len(fileSize) >= (data.size)*numbits:
        print('Input is too long to be hidden within the image. ')
        return 

    # insert the file size
    occupied = set()
    for i, row in enumerate(data):
        if complete:
            break
        for j, column in enumerate(row):
            if complete:
                break
            for k in range(len(column)):
                if index > len(fileSize)-1: 
                    complete = True
                    break
                
                if twoBits:
                    column[k] = insertTwoBits(column[k], fileSize, index)
                else:
                    column[k] = insertBit(column[k], fileSize, index)
                
                occupied.add((i,j,k))
                index += numbits

    pixelPositions = createSet(data, len(binString)//numbits, occupied)
    index = 0
    for pos in pixelPositions:
        if twoBits:
            data[pos] = insertTwoBits(data[pos], binString, index)
        else:
            data[pos] = insertBit(data[pos], binString, index)
        updateVariable(index, len(binString))
        index += numbits
    
    updateVariable(0,0)
    new = Image.fromarray(data)
    new.save(outputFileName)
    os.remove("temp.png")


def decodeRandomly(inputFile, twoBits=True):
    numBits = 2 if twoBits else 1
    out = ''
    size = ''
    data = np.array(Image.open(inputFile))
    complete = False
    index = 0
    occupied = set()

    for i, row in enumerate(data):
        if complete:
            break
        for j, column in enumerate(row):
            if complete:
                break
            for k in range(len(column)):
                size += int2bin(column[k])[-numBits:]
                index += numBits
                occupied.add((i,j,k))
                if not len(size)%8 and size[-8:] == int2bin(0):
                    size = getFileInt(size)
                    complete = True
                    break

    pixelPositions = createSet(data, size//numBits, occupied)

    for pos in pixelPositions:
        out += int2bin(data[pos])[-numBits:]
        updateVariable(len(out), len(pixelPositions))
    
    updateVariable(0,0)
    return bin2txt(out)


###################################################################################################################################
# tkinter GUI section begins here

class gui:
    def __init__(self, root, load):
        self.root = root
        self.root.geometry('500x500')
        self.root.resizable(0,0)
        self.decode = BooleanVar()
        self.stegType = BooleanVar()
        self.randomInsertion = BooleanVar()
        
        # textvariable=self.load
        self.loading = Label(self.root, textvariable=load, width=100)
        self.loading.place(relx=.5, rely=.9, anchor=CENTER)
        
        self.r1 = Radiobutton(self.root, text="Encode", variable=self.decode, value=0, command=lambda:self.encodeOrdecode())
        self.r2 = Radiobutton(self.root, text="Decode", variable=self.decode, value=1, command=lambda:self.encodeOrdecode())

        self.r1.place(relx=0.35, rely=0.1, anchor=CENTER)
        self.r2.place(relx=0.65, rely=0.1, anchor=CENTER)        
        self.r3 = Radiobutton(self.root, text="Text Stego", variable=self.stegType, value=0, command=lambda:self.getStegoType())
        self.r4 = Radiobutton(self.root, text="Hidden Image", variable=self.stegType, value=1, command=lambda:self.getStegoType())
        self.r3.place(relx=0.35, rely=0.15, anchor=CENTER)
        self.r4.place(relx=0.65, rely=0.15, anchor=CENTER)
        self.input = entry(self.root, 'Input Image:', 'Open Image', .2, (("jpeg files","*.jpg"),('PNG files', '*.png'),("all files","*.*")), place=True)
        
        self.text = entry(self.root, 'Input Text File', 'Input Text', .3, [('txt files', '*.txt')], place=True)
        self.secondImg = entry(self.root, 'Image To be Hidden', 'Open Image', .3, (("jpeg files","*.jpg"),('PNG files', '*.png'),("all files","*.*")))

        self.saveLoc = entry(self.root, 'Save Location', 'Save As', .4, (('PNG files', '*.png'),("all files","*.*")), Open=False, place=True)

        self.numBits = radio(self.root, .5, '1 Bit', '2 Bits', 'Number of Bits', place=True)

        self.checkBox = Checkbutton(self.root, variable=self.randomInsertion, text='Random Bit Insertion')
        self.checkBox.place(relx=.5, rely=.62, anchor=CENTER)

        self.encodingList = [self.text, self.secondImg]

        self.runButton = Button(self.root, text='Run', command=self.run)
        self.runButton.place(relx=.5, rely=.8, anchor=CENTER)

        self.root.mainloop()
    
    def encodeOrdecode(self):
        if self.decode.get():
            # Decode
            for widget in self.encodingList:
                if widget.isPlaced:
                    widget.remove()
            self.saveLoc.move(.3)
            self.numBits.move(.4)
            self.checkBox.place_configure(relx=.5, rely=.5, anchor=CENTER)
            self.getStegoType()
        else:
            # Encode
            self.saveLoc.move(.4)
            self.numBits.move(.5)
            for widget in self.encodingList:
                widget.place()
            self.getStegoType()

    def getStegoType(self):
        if not self.decode.get():
            # Encoding
            if self.stegType.get():
                # Imgage
                self.text.remove()
                self.numBits.remove()
                self.checkBox.place_forget()
                self.secondImg.place()

            else:
                # Text
                self.text.place()
                self.secondImg.remove()
                self.numBits.place()
                self.checkBox.place(relx=.5, rely=.62, anchor=CENTER)
                
        else:
            # Decoding
            if self.stegType.get():
                # Image
                self.checkBox.place_forget()
                self.numBits.remove()
            else:
                # Text
                self.checkBox.place(relx=.5, rely=.5, anchor=CENTER)
                self.numBits.place()

    def run(self):
        # ENCODE
        # print(getLoading())
        
        if not self.decode.get():
            # image insertion
            if self.stegType.get():
                # print(getLoading())
                imgInImg(self.input.data.get(), self.secondImg.data.get(), self.saveLoc.data.get())

            # text insertion
            else:
                # random insertion
                if self.randomInsertion.get():
                    insertRandomly(self.input.data.get(), self.text.data.get(), self.saveLoc.data.get(), twoBits=self.numBits.data.get(), stringInput=False)
                # regular insertion
                else:
                    encode(self.input.data.get(), self.text.data.get(), self.saveLoc.data.get(), twoBits=self.numBits.data.get(), stringInput=False)
        # DECODE
        else:
            # image from image
            if self.stegType.get():
                getImgFromImg(self.input.data.get(), self.saveLoc.data.get())

            # text insertion
            else:
                # random decode
                if self.randomInsertion.get():
                    with open(self.saveLoc.data.get(), 'w') as output:
                        output.write(decodeRandomly(self.input.data.get(), self.numBits.data.get()))
                # regular decode
                else:
                    with open(self.saveLoc.data.get(), 'w') as output:
                        output.write(decode(self.input.data.get(), self.numBits.data.get()))
class entry:
    def __init__(self, root , infoText, buttonTXT, y, fileTypes,  Open=True, place=False):
        self.y = y
        self.data = StringVar()
        self.isPlaced = place
        self.infoText = StringVar()
        self.infoText.set(infoText)

        self.buttonTxt = StringVar()
        self.buttonTxt.set(buttonTXT)


        self.info = Label(root, textvariable=self.infoText)
        
        if Open:
            self.button = Button(root, textvariable=self.buttonTxt, command=self.getFileLoc)
        else:
            self.button = Button(root, textvariable=self.buttonTxt, command=self.getSaveLoc)

        self.label = Label(root, textvariable=self.data, width=len(self.data.get()), anchor=W, justify=LEFT)

        # for holding file type for search functions list
        self.fileTypes = fileTypes

        if place:
            self.place()

    def getFileLoc(self):
        self.data.set(filedialog.askopenfilename(initialdir = "./",title = "Select file",filetypes =self.fileTypes))
    # only save as png
    def getSaveLoc(self):
        self.data.set(filedialog.asksaveasfilename(initialdir = "./",title = "Select file",defaultextension='.png', filetypes=[('PNG files', '*.png')]))
    
    def remove(self):
        self.isPlaced = False
        self.data.set('')
        self.label.place_forget()
        self.info.place_forget()
        self.button.place_forget()

    def place(self):
        self.isPlaced = True
        self.info.place(relx=.5, rely=self.y, anchor=CENTER)
        self.button.place(relx=.1, rely=(self.y+.05), anchor=CENTER)
        self.label.place(relx=.2, rely=(self.y+.05), anchor=W, relwidth=.70)
        print(self.label.winfo_width())

    def move(self, y):
        self.remove()
        self.y = y
        self.place()

class radio:
    def __init__(self, root, y, label1, label2, info, place=False):
        self.data = BooleanVar()
        self.isPlaced = place
        self.y = y
        self.info = Label(root, text=info)
        self.b1 = Radiobutton(root, text=label1, variable=self.data, value=0)
        self.b2 = Radiobutton(root, text=label2, variable=self.data, value=1)
        if place:
            self.place()
    
    def remove(self):
        self.isPlaced = False
        self.data.set(0)
        self.info.place_forget()
        self.b1.place_forget()
        self.b2.place_forget()

    def place(self):
        self.isPlaced = True
        self.info.place(relx=.5, rely=self.y, anchor=CENTER)
        self.b1.place(relx=0.40, rely=(self.y + .05), anchor=CENTER)
        self.b2.place(relx=0.60, rely=(self.y + .05), anchor=CENTER)
    
    def move(self, y):
        self.remove()
        self.y = y
        self.place()


def updateVariable(var, n):
    if var and n:
        out = '='* round(((var+1)/n) *10)
        out = '['+ out + '-'*(10-len(out)) + ']'
        if out != loadingBar.get():
            loadingBar.set(out)
            root.update()
    else:
        loadingBar.set('Sucess!')
        root.update()
        

test = gui(root, loadingBar)