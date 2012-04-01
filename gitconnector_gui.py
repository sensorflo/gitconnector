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
        self.release = Button(frame, text="relase", command=self.release_button)
        self.release.pack(side=LEFT)
        self.release = Button(frame, text="commit", command=self.commit_button)
        self.release.pack(side=LEFT)
        self.pull = Button(frame, text="pull (get)", command=self.pull_button)
        self.pull.pack(side=LEFT)
        self.make_nice = Button(frame, text="make branch nice", command=self.make_branch_nice_button)
        self.make_nice.pack(side=LEFT)
        self.make_nice = Button(frame, text="update status", command=self.update_status_button)
        self.make_nice.pack(side=LEFT)

        textfr=Frame(frame)
        self.text=Text(textfr,background='white') # height=25,width=100,
       	# put a scroll bar in the frame
        scroll=Scrollbar(textfr)
        self.text.configure(yscrollcommand=scroll.set)
        # self.text.config(state=DISABLED)
		
        #pack everything
        self.text.pack(side=LEFT)
        scroll.pack(side=RIGHT,fill=Y)
        textfr.pack(side=BOTTOM)

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
            self.text.delete("0.0",END)
            self.text.insert(END, gitconnector.get_status_txt())
        except Exception as e:
            tkMessageBox.showwarning("error",e)


root = Tk()
root.wm_title("git connector")
app = App(root)
root.mainloop()

