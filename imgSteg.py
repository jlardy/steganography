import numpy as np
from PIL import Image 
import os
from utils import *

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
    # img2 = Image.fromarray(img2)
    img1.save('temp.png', optimized=True, quality=95)
    # img2.save('temp2.png', optimized=True, quality=95)
    img1 = np.array(Image.open('temp.png'))
    # img2 = np.array(Image.open('temp2.png'))
    
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
            print('Success!')
            break
        for column in row:
            if index > len(redStr)-1:
                stop = True
                break
            column[0] = insertTwoBits(column[0], redStr, index)
            column[1] = insertTwoBits(column[1], greenStr, index)
            column[2] = insertTwoBits(column[2], blueStr, index)
            index += 2

    new = Image.fromarray(img1)
    new.save(outputFileName)
    os.remove("temp.png")
    # os.remove("temp2.png")

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
                if len(rStr) == size:
                    stop = True
                    break
    
    # build the image from lists of ints converted from the binary strings by calling intArray function 
    out = np.stack((intArrayFromBin(rStr),intArrayFromBin(gStr),intArrayFromBin(bStr)),axis=1)
    out = np.reshape(out, (length, width, 3))
    # convert form an aray to image and save
    new = Image.fromarray(out.astype('uint8'))
    new.save(outputFileName)

