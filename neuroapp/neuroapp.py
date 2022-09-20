from tkinter import *
from tkinter import ttk
import re
import cv2
import PIL
from PIL import Image,ImageTk

"""
    An application for matching a person with their photo, retrieved with their given ID.
    A program must receive a photo through a "load photo" button (available after user pressed "take photo" button) and an ID in the form of a e-mail through a "enter ID" button.
    Then photo is (processed?) | saved as cur.png and can be accesed in the main folder.
    
    Requirements:
        - active camera 
        - python 3+
        - re (default?)
        - PIL (default?)
        - tkinter (default?)
        - opencv-python
        - opencv-contrib-python
        - ...
        
    Structure of application:
        - root (main/base window)
            - cameraFrame (left part of the screen. Responsible for getting image and displaying the result)
                - camera
                - takePhotoButton
                - retakePhotoButton
                - loadPhotoButton
                - resultLabel
            - idFrame (right part of the screen. Responsible for getting an ID and starting the matching)
                - idLabel
                - idEntry
                - idButton
                - startButton
                - startLabel
            
    TODO:
    1) rewrite in the format of OOP
    2) add comment inside code
    3) tweak with grids and styles
    4) add HELP menu?
    5) make main window properly scalable after resizing
    6) add config panel?
    7) exhaustive list of requirements
    8) use ID to retrieve original photo
    9) send loaded and original photos to neural network
    10) display results from neural network (how?)
    11) ...
"""

#initialization
root = Tk()
root.title("neuroapp")
cameraFrame = ttk.Frame(root, padding = 15, borderwidth = 2, relief = "ridge")
idFrame = ttk.Frame(root, padding = 15, borderwidth = 2, relief = "ridge")

s = ttk.Style()
s.configure("General.TButton", font = "helvetica 10")
s.configure("StatusOFF.TButton", font = "helvetica 10", background = "#C73423", foreground = "#C73423")
s.configure("StatusON.TButton", font = "helvetica 10", background = "#47B630", foreground = "#306F23")

#button functions
def checkId(value):
    valid = re.match(r"^([a-zA-Z0-9][!#$%&'*+-/=?^_`{|+.]?)+@([a-zA-Z0-9][-.]?)+\.([a-z]+)$", value) is not None
    idButton.state(["!disabled"] if valid else ["disabled"])
    idReady.set(False)
    idButton.configure(style = "StatusOFF.TButton")
    startButton.state(["disabled"])
    return True
checkIdWrapper = (idFrame.register(checkId), "%P")
        
def idButtonPressed():
    idReady.set(True)
    idButton.configure(style = "StatusON.TButton")
    startButton.state(["!disabled"] if idReady.get() and photoReady.get()
                      else ["disabled"])

def takePhoto():
    imageTaken.set(True)
    takePhotoButton.state(["disabled"])
    retakePhotoButton.state(["!disabled"])
    loadPhotoButton.state(["!disabled"])
    

def retakePhoto():
    imageTaken.set(False)
    takePhotoButton.state(["!disabled"])
    retakePhotoButton.state(["disabled"])
    loadPhotoButton.state(["disabled"])
    photoReady.set(False)
    loadPhotoButton.configure(style = "StatusOFF.TButton")
    startButton.state(["disabled"])
    show_frame()

def loadPhoto():
    camera.imgtk._PhotoImage__photo.write("cur.png")
    photoReady.set(True)
    loadPhotoButton.configure(style = "StatusON.TButton")
    startButton.state(["!disabled"] if idReady.get() and photoReady.get()
                      else ["disabled"])
    
#setting up the camera
cascPath = "./Resources/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
    
width, height = 256, 256
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

def show_frame():
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=13,
        minSize=(40, 40),
        flags= cv2.CASCADE_SCALE_IMAGE
    )
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (240, 240, 240), 2)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    
    img = PIL.Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    camera.imgtk = imgtk
    camera.configure(image = imgtk)
    if not imageTaken.get():
        camera.after(30, show_frame)
                   
#cameraFrame
camera = Label(cameraFrame)
camera.grid(column = 0, row = 0, columnspan = 3, sticky = (N, W, E, S))

imageTaken = BooleanVar(value = False)

takePhotoButton = ttk.Button(cameraFrame, text = "Take photo", command = lambda: takePhoto(),
                             state = ["!disabled"], style = "General.TButton")
takePhotoButton.grid(column = 0, row = 1)

retakePhotoButton= ttk.Button(cameraFrame, text = "Retake photo", command = lambda: retakePhoto(),
                              state = ["disabled"], style = "General.TButton")
retakePhotoButton.grid(column = 1, row = 1)

photoReady = BooleanVar(value = False)
loadPhotoButton = ttk.Button(cameraFrame, text = "Load photo", command = lambda: loadPhoto(),
                             state = ["disabled"], style = "StatusOFF.TButton")
loadPhotoButton.grid(column = 2, row = 1)

resultLabel = ttk.Label(cameraFrame, text = "Result?", anchor = "center",
                        font = "helvetica 22", background = "#e4e4e4", foreground = "#606060")
resultLabel.grid(column = 0, row = 2, columnspan = 3, sticky = (N, S, E, W), padx = 10, pady = 15, ipadx = 5, ipady = 10)

#idFrame
idLabel = ttk.Label(idFrame, text = "Enter an ID:", font = "helvetica 14")
idLabel.grid(column = 0, row = 0, padx = 10, pady = 10)

idValue = StringVar()

idEntry = ttk.Entry(idFrame, textvariable = idValue, width = 25, validate = "key",
                    validatecommand = checkIdWrapper)
idEntry.grid(column = 0, row = 1, padx = 10, pady = 10)

idReady = BooleanVar(value = False)
idButton = ttk.Button(idFrame, text = "Enter ID", command = lambda: idButtonPressed(),
                      state = ["disabled"], style = "StatusOFF.TButton")
idButton.grid(column = 0, row = 2, padx = 10, pady = 10)

startButton = ttk.Button(idFrame, text = "Start matching", command = lambda: print("Started comparison"),
                         state = ["disabled"], style = "General.TButton")
startButton.grid(column = 0, row = 3, padx = 10, pady = 10)

startLabel = ttk.Label(idFrame, text = "Enter ID and load a photo to start", font = "helvetica 16")
startLabel.grid(column = 0, row = 4, padx = 10)

#Layout configuration of frames
cameraFrame.grid_columnconfigure(0, weight = 1)
cameraFrame.grid_columnconfigure(1, weight = 1)
cameraFrame.grid_columnconfigure(2, weight = 1)
cameraFrame.grid_rowconfigure(0, weight = 5)
cameraFrame.grid_rowconfigure(1, weight = 1)
cameraFrame.grid_rowconfigure(2, weight = 2)
cameraFrame.grid(column = 0, row = 0, sticky = (N, W, E, S))
idFrame.grid(column = 1, row = 0, sticky = (N, W, E, S))

root.grid_columnconfigure(0, weight = 2)
root.grid_rowconfigure(0, weight = 1)
root.grid_columnconfigure(1, weight = 1)

show_frame()
root.mainloop()
