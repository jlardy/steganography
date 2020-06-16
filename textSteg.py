import numpy as np
from PIL import Image 
import os
import random
from utils import *

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

    
    new = Image.fromarray(data)
    new.save(outputFileName)
    os.remove("temp.png")


# decodes an input file that has been previously encoded 
def decode(inputFile, twoBits=False):
    if twoBits:
        numBits = 2
    else:
        numBits = 1
    
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
                    if len(out) == size:
                        stop = True
                        text=True
                        break

    if text:
        return bin2txt(out)
    else:
        print('No text found.')


def createSet(imgArr, binMessageLength, occupied):
    positions = set()
    length, width, dimensions = imgArr.shape
    random.seed(length)

    while len(positions) != binMessageLength:
        newPos = (random.randint(0,length-1), random.randint(0,width-1), random.randint(0,dimensions-1))
        if newPos not in occupied:
            positions.add(newPos)
    return positions

def insertRandomly(inputFile, inString, outputFileName='out.png', twoBits=True):
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
        index += numbits
    
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
    
    return bin2txt(out)


