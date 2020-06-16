from tkinter import filedialog
from tkinter import *
from main import *
from imgSteg import *
from textSteg import *

class gui:
    def __init__(self):
        self.root = Tk()
        self.root.geometry('500x500')
        self.root.resizable(0,0)
        self.decode = BooleanVar()
        self.stegType = BooleanVar()
        self.randomInsertion = BooleanVar()
        
        Radiobutton(self.root, text="Encode", variable=self.decode, value=0, command=lambda:self.encodeOrdecode()).place(relx=0.35, rely=0.1, anchor=CENTER)
        Radiobutton(self.root, text="Decode", variable=self.decode, value=1, command=lambda:self.encodeOrdecode()).place(relx=0.65, rely=0.1, anchor=CENTER)
                
        Radiobutton(self.root, text="Text Stego", variable=self.stegType, value=0, command=lambda:self.getStegoType()).place(relx=0.35, rely=0.15, anchor=CENTER)
        Radiobutton(self.root, text="Hidden Image", variable=self.stegType, value=1, command=lambda:self.getStegoType()).place(relx=0.65, rely=0.15, anchor=CENTER)

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
        print(
        'Encode:',self.decode.get(), '\n',
        'StegType:',self.stegType.get(), '\n',
        'Random Insertion:',self.randomInsertion.get(), '\n',
        'Input Image:',self.input.data.get(), '\n',
        'Text File Path:',self.text.data.get(), '\n',
        'Second Image Path:',self.secondImg.data.get(), '\n',
        'Save Location:',self.saveLoc.data.get(),'\n',
        'NumBits:',self.numBits.data.get())

        # encode
        # decode
        # insertRandomly
        # decodeRandomly
        # imgInImg
        # getImgFromImg
        
        # ENCODE
        if not self.decode.get():
            # image insertion
            if self.stegType.get():
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
                        print(decode(self.input.data.get(), self.numBits.data.get()))
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

        self.label = Label(root, textvariable=self.data, width=len(self.data.get()))

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
        self.label.place(relx=.5, rely=(self.y+.05), anchor=CENTER)

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


run = gui()