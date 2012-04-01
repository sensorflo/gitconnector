#!/usr/bin/python2.7
# gui for accessing functionality in git_dragon.py

from Tkinter import *
import tkMessageBox
import gitconnector

# release 
#   make nice
#   pull
#     fetch
#     merge/rebase
#   push  
#
# Always on top level: commit
#
#
# Show in status pane. That is neccessairy to no a bit where you are. Without
# any info, it feels very free floating. But keep it very dump! Use other GUIs
# for more convenient info.
# - git status, i.e added/deleted/changed files
# - no of pushable commits on nice branch,
# - no of nice-able commits on free branch
# - git log --graph --oneline 
# 


class App:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.text=Text(master,background='white',height=25) # height=25,width=100,
        self.text.config(state=DISABLED)
        self.text.pack(expand=1,fill=BOTH,side=TOP)
        # self.text.scrolly=Scrollbar(self.text)
        # self.text.configure(yscrollcommand=self.text.scrolly.set) 
        # self.text.scrolly.pack(side=RIGHT,fill=Y)
        # self.text.scrollx=Scrollbar(self.text)
        # self.text.configure(xscrollcommand=self.text.scrollx.set) 
        # self.text.scrollx.pack(side=BOTTOM,fill=X)

        self.release = Button(frame, text="relase", command=self.release_button)
        self.release.pack(side=LEFT)
        self.commit = Button(frame, text="commit", command=self.commit_button)
        self.commit.pack(side=LEFT)
        self.pull = Button(frame, text="pull (get)", command=self.pull_button)
        self.pull.pack(side=LEFT)
        self.make_nice = Button(frame, text="make branch nice", command=self.make_branch_nice_button)
        self.make_nice.pack(side=LEFT)
        self.update_status = Button(frame, text="update status", command=self.update_status_button)
        self.update_status.pack(side=LEFT)
        self.update_status_button()

    # as the old 'release'
    def release_button(self):
        try:
            gitconnector.release()
            self.update_status_button()
            tkMessageBox.showinfo("done","done")
        except Exception as e:
            tkMessageBox.showwarning("error",e)

    # as the old 'release'
    def commit_button(self):
        try:
            gitconnector.commit(True)
            self.update_status_button()
            tkMessageBox.showinfo("done","done")
        except Exception as e:
            tkMessageBox.showwarning("error",e)

    # 
    def make_branch_nice_button(self):
        try:
            gitconnector.make_branch_nice(explicit=True)
            self.update_status_button()
            tkMessageBox.showinfo("done","done")
        except Exception as e:
            tkMessageBox.showwarning("error",e)

    # aka the old 'get'
    # can easily be done by other GUIs
    def pull_button(self):
        try:
            gitconnector.pull(explicit=True)
            self.update_status_button()
            tkMessageBox.showinfo("done","done")
        except Exception as e:
            tkMessageBox.showwarning("error",e)

    def update_status_button(self):
        try:
            txt = gitconnector.get_status_txt()
            self.text.config(state=NORMAL)
            self.text.delete("0.0",END)
            self.text.insert(END, txt )
            self.text.config(state=DISABLED)
        except Exception as e:
            tkMessageBox.showwarning("error",e)


root = Tk()
root.wm_title("git connector")
app = App(root)
root.mainloop()

