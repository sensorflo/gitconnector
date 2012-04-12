#!/usr/bin/python2.7
# gui for accessing gitconnector.py
# See file README for info what gitconnector is

from Tkinter import *
import tkMessageBox, tkFileDialog, Tkinter
import gitconnector
import os
import re
import git

# window title shall contain an abbreviated current working directory
def set_window_title():
    h = os.environ['HOME']
    if h[-1] != "/":
        h += "/"
    prefixes = [ h + "drives/xp/Projects/DieBonder/", h + "src/", h ]
    cwd = os.getcwd()
    for x in prefixes:
        cwd = re.sub( re.escape(x), "", cwd ) 
    root.wm_title("git connector : " + cwd )

class App:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.text=Text(master,background='white',height=25,wrap=NONE) # height=25,width=100,
        self.text.config(state=DISABLED)
        self.text.pack(expand=1,fill=BOTH,side=TOP)
        # self.text.scrolly=Scrollbar(self.text)
        # self.text.configure(yscrollcommand=self.text.scrolly.set) 
        # self.text.scrolly.pack(side=RIGHT,fill=Y)
        # self.text.scrollx=Scrollbar(self.text)
        # self.text.configure(xscrollcommand=self.text.scrollx.set) 
        # self.text.scrollx.pack(side=BOTTOM,fill=X)

        also_with_other = "You can do the same, maybe even more conveniently, with any other git frontend (tortoiseGit, SmartGit, ...)"

        self.publish = Button(frame, text="Publish", command=self.publish_button)
        self.publish.pack(side=LEFT)
        ToolTip(self.publish, text='Publish your local work work. Is composed of 1) Commit 2) Pull 3) Make free branch nice 4) Push nice branch. Loosly corresponds to VssConnectors "Build Release"')
        self.commit = Button(frame, text="Commit", command=self.commit_button)
        self.commit.pack(side=LEFT)
        # todo: change tooltip in case of rebase
        ToolTip(self.commit, text='This button has multiple functions\n\nWhen labeled commit: Commits your changes of the working tree and/or the index into the current branch.\n\nWhen labeled continue rebase: After you manually resolved merge conflicts while being in a rebase, this continues the rebase.\n\n' + also_with_other )
        self.pull = Button(frame, text="Pull", command=self.pull_button)
        self.pull.pack(side=LEFT)
        ToolTip(self.pull, text='1) Fetches any new commits of the remote repo 2) Merges branch origin/master into your free branch 3) Rebases (similar to merging) your nice branch onto origin/master. Loosly corresponds to VssConnectors "Get Latest"')
        self.make_nice = Button(frame, text="Make branch nice", command=self.make_branch_nice_button)
        self.make_nice.pack(side=LEFT)
        ToolTip(self.make_nice, text='Creates/updates the nice branch using the free branch. That squashes all (un-verifified) commits of the free branch in one single verified commit on the nice branch. A commit on the nice branch only succeeds if it passes our verification (e.g it must compile).')
        self.abort = Button(frame, text="Abort", command=self.abort_button)
        self.abort.pack(side=LEFT)
        ToolTip(self.abort, text="Aborts a running merge / rebase / am (apply-mailbox) and brings you back to the state before the merge / rebase / am. " + also_with_other )
        self.update_status = Button(frame, text="Update Status", command=self.update_status_button)
        self.update_status.pack(side=LEFT)
        ToolTip(self.update_status, text='Updates the content of the status pane')
        self.help = Button(frame, text="Help Out", command=self.help_out)
        self.help.pack(side=LEFT)
        ToolTip(self.help, text="Helps you out when you're in trouble. Analyzes your repo and report when it is not in an normal state and gives tips what to do about it.")

        self.menubar = Menu(master)

        self.filemenu = Menu(self.menubar,tearoff=0)
        self.filemenu.add_command( label='Open Repo ...', command=self.open_button)
        # ToolTip(self.open, text='Open another git repo to work with.')
        self.filemenu.add_separator()
        self.filemenu.add_command( label='Exit', command=master.quit)
        self.menubar.add_cascade(label='File', menu=self.filemenu)

        self.helpmenu = Menu(self.menubar,tearoff=0)
        self.helpmenu.add_command( label='Help', command=self.help_browser)
        self.helpmenu.add_command( label='About Gitconnector', command=self.about)
        self.menubar.add_cascade(label='Help', menu=self.helpmenu)

        master.config(menu=self.menubar)

        # todo: button to launch external tool for history / status-working-tree

        # in dummy mode:
        # - only commit & publish
        # - status pane contains tips what to do next. E.g.
        # -   you have local changes, you can commit them.
        # -   you have local commits on the free branch. You can publish them
        # -   the remote repo has new commits. You can update yourself with them.
        # -   you're in merge conflict, you can...

        self.update_status_button()

    def open_button(self):
        try:
            repo_path = tkFileDialog.askdirectory(title='open git repository')
            if len(repo_path)==0:
                return
            if not git.is_repo(repo_path):
                tkMessageBox.showerror("","Not a git repository")
                return
            os.chdir(repo_path)
            set_window_title()
            self.update_status_button()
        except Exception as e:
            tkMessageBox.showwarning("error",e)

    # as the old 'release'
    def publish_button(self):
        try:
            gitconnector.publish(explicit=True)
            self.update_status_button()
            tkMessageBox.showinfo("done","done")
        except Exception as e:
            tkMessageBox.showwarning("error",e)

    def commit_button(self):
        try:
            gitconnector.commit_or_continue(explicit=True)
            self.update_status_button()
            tkMessageBox.showinfo("done","done")
        except Exception as e:
            tkMessageBox.showwarning("error",e)

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

    def abort_button(self):        
        try:
            gitconnector.abort(explicit=True)
            self.update_status_button()
            tkMessageBox.showinfo("done","done")
        except Exception as e:
            tkMessageBox.showwarning("error",e)

    def update_status_button(self):
        try:
            (txt,status) = gitconnector.get_status()
            self.text.config(state=NORMAL)
            self.text.delete("0.0",END)
            self.text.insert(END, txt )
            self.text.config(state=DISABLED)
            print status
            if status==git.repo().REBASE:
                self.commit.config(text = "continue rebase")
            else:
                self.commit.config(text = "commit")

        except Exception as e:
            tkMessageBox.showwarning("error",e)

    def help_browser(self):
        tkMessageBox.showinfo("Help","Not implemented yet. Intended to startup browser with git and gitconnector help/manual pages")

    def about(self):
        tkMessageBox.showinfo("About Gitconnector","gitconnector version " + gitconnector.version())

    def help_out(self):
        try:
            txt = gitconnector.help(explicit=True)
        except Exception as e:
            tkMessageBox.showwarning("error",e)


# '''Michael Lange <klappnase (at) freakmail (dot) de>
# The ToolTip class provides a flexible tooltip widget for Tkinter; it is based on IDLE's ToolTip
# module which unfortunately seems to be broken (at least the version I saw).
# INITIALIZATION OPTIONS:
# anchor :        where the text should be positioned inside the widget, must be on of "n", "s", "e", "w", "nw" and so on;
#                 default is "center"
# bd :            borderwidth of the widget; default is 1 (NOTE: don't use "borderwidth" here)
# bg :            background color to use for the widget; default is "lightyellow" (NOTE: don't use "background")
# delay :         time in ms that it takes for the widget to appear on the screen when the mouse pointer has
#                 entered the parent widget; default is 500
# fg :            foreground (i.e. text) color to use; default is "black" (NOTE: don't use "foreground")
# follow_mouse :  if set to 1 the tooltip will follow the mouse pointer instead of being displayed
#                 outside of the parent widget; this may be useful if you want to use tooltips for
#                 large widgets like listboxes or canvases; default is 0
# font :          font to use for the widget; default is system specific
# justify :       how multiple lines of text will be aligned, must be "left", "right" or "center"; default is "left"
# padx :          extra space added to the left and right within the widget; default is 4
# pady :          extra space above and below the text; default is 2
# relief :        one of "flat", "ridge", "groove", "raised", "sunken" or "solid"; default is "solid"
# state :         must be "normal" or "disabled"; if set to "disabled" the tooltip will not appear; default is "normal"
# text :          the text that is displayed inside the widget
# textvariable :  if set to an instance of Tkinter.StringVar() the variable's value will be used as text for the widget
# width :         width of the widget; the default is 0, which means that "wraplength" will be used to limit the widgets width
# wraplength :    limits the number of characters in each line; default is 150

# WIDGET METHODS:
# configure(**opts) : change one or more of the widget's options as described above; the changes will take effect the
#                     next time the tooltip shows up; NOTE: follow_mouse cannot be changed after widget initialization

# Other widget methods that might be useful if you want to subclass ToolTip:
# enter() :           callback when the mouse pointer enters the parent widget
# leave() :           called when the mouse pointer leaves the parent widget
# motion() :          is called when the mouse pointer moves inside the parent widget if follow_mouse is set to 1 and the
#                     tooltip has shown up to continually update the coordinates of the tooltip window
# coords() :          calculates the screen coordinates of the tooltip window
# create_contents() : creates the contents of the tooltip window (by default a Tkinter.Label)
# '''
# Ideas gleaned from PySol

class ToolTip:
    def __init__(self, master, text='Your text here', delay=500, **opts):
        self.master = master
        self._opts = {'anchor':'center', 'bd':1, 'bg':'lightyellow', 'delay':delay, 'fg':'black',\
                      'follow_mouse':0, 'font':None, 'justify':'left', 'padx':4, 'pady':2,\
                      'relief':'solid', 'state':'normal', 'text':text, 'textvariable':None,\
                      'width':0, 'wraplength':150}
        self.configure(**opts)
        self._tipwindow = None
        self._id = None
        self._id1 = self.master.bind("<Enter>", self.enter, '+')
        self._id2 = self.master.bind("<Leave>", self.leave, '+')
        self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
        self._follow_mouse = 0
        if self._opts['follow_mouse']:
            self._id4 = self.master.bind("<Motion>", self.motion, '+')
            self._follow_mouse = 1
    
    def configure(self, **opts):
        for key in opts:
            if self._opts.has_key(key):
                self._opts[key] = opts[key]
            else:
                KeyError = 'KeyError: Unknown option: "%s"' %key
                raise KeyError
    
    ##----these methods handle the callbacks on "<Enter>", "<Leave>" and "<Motion>"---------------##
    ##----events on the parent widget; override them if you want to change the widget's behavior--##
    
    def enter(self, event=None):
        self._schedule()
        
    def leave(self, event=None):
        self._unschedule()
        self._hide()
    
    def motion(self, event=None):
        if self._tipwindow and self._follow_mouse:
            x, y = self.coords()
            self._tipwindow.wm_geometry("+%d+%d" % (x, y))
    
    ##------the methods that do the work:---------------------------------------------------------##
    
    def _schedule(self):
        self._unschedule()
        if self._opts['state'] == 'disabled':
            return
        self._id = self.master.after(self._opts['delay'], self._show)

    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self.master.after_cancel(id)

    def _show(self):
        if self._opts['state'] == 'disabled':
            self._unschedule()
            return
        if not self._tipwindow:
            self._tipwindow = tw = Tkinter.Toplevel(self.master)
            # hide the window until we know the geometry
            tw.withdraw()
            tw.wm_overrideredirect(1)

            if tw.tk.call("tk", "windowingsystem") == 'aqua':
                tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

            self.create_contents()
            tw.update_idletasks()
            x, y = self.coords()
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.deiconify()
    
    def _hide(self):
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()
                
    ##----these methods might be overridden in derived classes:----------------------------------##
    
    def coords(self):
        # The tip window must be completely outside the master widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        # or we take care that the mouse pointer is always outside the tipwindow :-)
        tw = self._tipwindow
        twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
        w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
        # calculate the y coordinate:
        if self._follow_mouse:
            y = tw.winfo_pointery() + 20
            # make sure the tipwindow is never outside the screen:
            if y + twy > h:
                y = y - twy - 30
        else:
            y = self.master.winfo_rooty() + self.master.winfo_height() + 3
            if y + twy > h:
                y = self.master.winfo_rooty() - twy - 3
        # we can use the same x coord in both cases:
        x = tw.winfo_pointerx() - twx / 2
        if x < 0:
            x = 0
        elif x + twx > w:
            x = w - twx
        return x, y

    def create_contents(self):
        opts = self._opts.copy()
        for opt in ('delay', 'follow_mouse', 'state'):
            del opts[opt]
        label = Tkinter.Label(self._tipwindow, **opts)
        label.pack()

# change working dir if requested
if len(sys.argv)>=2:
    os.chdir(sys.argv[1])

root = Tk()
set_window_title()
app = App(root)
root.mainloop()

