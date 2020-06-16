import sys

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


def query_yes_no(question, default="yes"):
    # Ask a yes/no question via raw_input() and return their answer.

    # "question" is a string that is presented to the user.
    # "default" is the presumed answer if the user just hits <Enter>.
    #     It must be "yes" (the default), "no" or None (meaning
    #     an answer is required of the user).

    # The "answer" return value is True for "yes" or False for "no".
    
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")