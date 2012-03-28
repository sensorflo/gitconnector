#!/usr/bin/python
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

# aka the old 'checkout'
def start_branch_button():
    try:
        # ask for branchname
        # if already exixts (check also the -nice sibling)
        # - either enter new name
        # - give existing name a suffix ala '-old-231'
        # they shall track origin/working
        gitconnector.start_branch()
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
        self.hi_there = Button(frame, text="start branch (checkout)", command=start_branch_button)
        self.hi_there.pack(side=LEFT)

        # if one wants to use other tools for the push/release process 
        self.hi_there = Button(frame, text="make branch nice", command=make_branch_nice_button)
        self.hi_there.pack(side=LEFT)
        # rebase/merge abort buttons?

root = Tk()
app = App(root)
root.mainloop()

