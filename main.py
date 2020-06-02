import numpy as np
from PIL import Image 
import os
from test import query_yes_no as query


# program adds this to the converted binary string 
delimeter = '111111111111111111111111111111111111111111111111'
# converting strings to binary strings 8 bit format
def str2bin(string): return ''.join(format(ord(i),'b').zfill(8) for i in string)

# converts the binary string back to unicode
def bin2txt(binstring): return ''.join([chr(int(binstring[i:i+8],2)) for i in range(0,len(binstring),8)])

# returns a list of integers from a binary string
def intArrayFromBin(binstring): return [int(binstring[i:i+8],2) for i in range(0,len(binstring),8)]

# converting intergers to 8 bit binary 
def int2bin(intInput): return '{0:08b}'.format(intInput)

# returns integer from 8 bit binary 
def bin2int(binstring): return int(binstring[0:8],2)


# SINGLE BIT INSERTION
def insertBit(integerInput, st, stIndex):
    converted = int2bin(integerInput)
    # pass in the pixel integer and the binary string, returns the integer 
    if converted[-1] == st[stIndex]:
        return bin2int(converted)
    else:
        converted = converted[:-1] + st[stIndex]
        return bin2int(converted)

# TWO BIT INSERTION
def insertTwoBits(integerInput, st, stIndex):
    converted = int2bin(integerInput)
    converted = converted[:-2] + st[stIndex] + st[stIndex+1] 
    return bin2int(converted)

def binaryFileSize(length):
    size = ''
    extra = '11111111'
    delim = '00000000'
    while length >= 255:
        size += extra
        length -= 255
    size += int2bin(length)
    size += delim
    return size

def getFileInt(binary):
    data = intArrayFromBin(binary)
    out = 0
    for integer in data:
        out += integer
    return out


# encodes a file, currently only works by exporting the image as a PNG
def encode(inputFile, inString, outputFileName='out.png', twoBits=False):
    complete = False
    remainder = False

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
    binString = str2bin(inString) + delimeter
    # print(len(binString))

    if twoBits:
        if len(binString) >= (data.size)*2:
            print('Input is too long to be hidden within the image. ')
            return 
        if len(binString)%2:
            print('REMAINDER')
            remainder = True
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
                    if remainder:
                        column[i] = insertBit(column[i], binString, index)
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
    out = ''
    counter = 0
    bre = False
    text = False
    # get the image
    data = np.array(Image.open(inputFile))
    # loop through and build a binary string from the lsb until the delimeter is included in the string 
    for row in data:
        if bre:
            break
        for column in row:
            if bre:
                break
            for i in range(len(column)):
                if twoBits:
                    out += int2bin(column[i])[-2]
                out += int2bin(column[i])[-1]
                counter += 1
                if delimeter in out:
                    bre = True
                    text = True
                    break
                elif counter > 100000:
                    bre = True 
                    break
    # if the delimeter was found print the string to the screen without the delimeter
    if text:
        print(bin2txt(out[0:len(out)-len(delimeter)]))
    else:
        print('No text found.')

def bruteForceOptimizer(desiredSize, length, width):
    # poorly written function, really unefficent but i couldnt think of a better way to do it. 
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
        answer = query('Whoops the image is too large to input, would you like to resize it?')
        
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
    new.save('foundImage.png')
    
    

imgInImg('rickRoll.jpg', 'rickRoll.png', 'lol.png')
getImgFromImg('lol.png')


# storing a text file in the image
# with open('rollText.txt', 'r') as txtfile:
#     mytextstring = txtfile.read()


# # hide text 
# encode('rickRoll.jpg', mytextstring)
# encode('pepe.png', '.', twoBits=True)
# # # read the encoded string from the output
# decode('foundImage.png')
