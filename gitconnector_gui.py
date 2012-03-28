#!/usr/bin/python2.7
# gui for accessing functionality in git_dragon.py

from Tkinter import *
import tkMessageBox
import gitconnector

# as the old 'release'
def release_button():
    try:
        gitconnector.release()
        tkMessageBox.showinfo("done","done")
    except Exception as e:
         tkMessageBox.showwarning("error",e)

# 
def make_branch_nice_button():
    try:
        gitconnector.make_branch_nice()
        tkMessageBox.showinfo("done","done")
    except Exception as e:
         tkMessageBox.showwarning("error",e)

# aka the old 'get'
# can easily be done by other GUIs
def pull_button():
    try:
        gitconnector.pull()
        tkMessageBox.showinfo("done","done")
    except Exception as e:
        tkMessageBox.showwarning("error",e)


class App:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        self.button = Button(frame, text="relase", command=release_button)
        self.button.pack(side=LEFT)
        self.hi_there = Button(frame, text="pull (get)", command=pull_button)
        self.hi_there.pack(side=LEFT)
        self.hi_there = Button(frame, text="make branch nice", command=make_branch_nice_button)
        self.hi_there.pack(side=LEFT)


root = Tk()
root.wm_title("git connector")
app = App(root)
root.mainloop()

