#!/usr/bin/python2.7
# Core functionality to tailor git for the dragon project

# responsibilities/goals, ordered after prio:
# - Central repo adheres to dragon guidelines.
# - Simple and easy standart use cases
#   - refine local state so it is 'nice' and thus pushable to central repo
#   - push to central repo
#   - pull from central repo
#   - all that for 'main' branch
# 
# - Local repo can be anything. The point of DVCS is to locally do whatever you like.
#   - However git dragon is only required to be able to work with a set of predefined states 
#   - Engineers should be allowed any git tool/frontend they like
# 
# - We don't have the (HW) infrastructure to do expensive compile test on the
#   central server side. Thus the compile test must remain, as with
#   vssconnector, on the client side.
# 
# - Does not undertake countermeassures against 'malicous' co-workers - we don't
#   have them. If somebody really want's to circumvent the checks he can do it
#   anyway.
#
# vssconnector was needed because vss is so bad. gitconnector is needed because
# a) git offers so many workflows
#

import subprocess
import re
import git
import tkMessageBox
git_binary = "/usr/bin/git"

default_branch = "master"
default_origin_branch = "remotes/origin/master"
nice_branch_regex = r'-nice$' # remember that both the nice and the ugly have a remote, so either of the two *has* two have a different name
nice_branch = "master-nice" # todo: rename nice -> (nothing)
ugly_branch = "master" # todo: rename ugly -> free
remote_branch = "origin/master"

# todo: rename sign-off to verified (according to git's option --no-verify) approved or certified or 
sign_off_str = "Signed-off-by: git-dragon"
no_verify_sign_off_str = "Signed-off-by: git-dragon no-verify"
help_msg = \
  '\n' +\
  '# title (until first empty line)\n' +\
  '#   - TDxxxx for all solved TDs \n' +\
  '#   - short and sweet and to the point; try to use less than 50 chars\n' +\
  '# body (the rest)\n' +\
  '#   - free format\n' +\
  '\n' 


def release():
    # pull before make_branch_nice, because after make_branch_nice we want have
    # low probability to have to merge again
    commit()
    repo = git.repo()
    repo.pull()
    make_branch_nice()
    repo.checkout(nice_branch)
    repo.push(nice_branch)
    repo.checkout(ugly_branch)
    repo.make_branch( unique_branch_name(ugly_branch) );
    repo.reset(nice_branch,"hard")

    # check_environment()
    # commit()
    # remote_has_changes = True # start with this assumption
    # while remote_has_changes:
    #     pull() 
    #     make_branch_nice()          # switches from ugly to nice branch
    #     remote_has_changes = push() # set remote_has_changes

def pull():
    repo = git.repo()

    commit()

    # update ugly_branch
    repo.checkout(ugly_branch)
    repo.pull()

    # update nice_branch todo: what if the above pull fails? Then the
    # nice_branch is not rebased which leads to troubles later
    repo.checkout(nice_branch)
    repo.rebase(remote_branch)

    # we want to continue working on ugly_branch
    repo.checkout(ugly_branch)

def get_status_txt():
    # todo: emphasise when in merge/rebase conflict
    repo = git.repo()
    txt = "--- status of index and working tree ---\n"
    txt += repo.get_status()
    txt += "\n"
    txt += "\n"
    txt += "--- current branch's friends ---\n"
    txt += "current branch: " + repo.current_branch() + "\n"
    txt += "remote branch : " + remote_branch + "\n" # x commits ahaed
    txt += "nice branch   : " + nice_branch + "\n"   # x commits pushable into remot
    txt += "free branch   : " + ugly_branch + "\n"   # x commits nice-able
    txt += "\n"
    txt += repo.get_log_graph(remote_branch,nice_branch,ugly_branch)
    # txt += "\nnice-able commits:\n"
    # txt += repo.
    # txt += "\npushable nice commits:\n"
    # txt += repo.
    return txt

def check_content():
    return

def check_test_suite_runs():
    return

def check_buildable():
    return

def check_message(message):
    return

def check_environment():
    # - git binary available
    # - no pending merges, rebases, ...
    # - remote repo available
    branches = subprocess.check_output([git_binary,"branch"]) # must be 'develop'
    current_branch = re.search(r'^\*\s+(\w+)',branches,re.M).group(1)
    if not (current_branch == default_branch):
        raise Exception("your current branch is '" + current_branch + "' " + \
                        "but it should be '" + default_branch + "'. Aborting")

    # remote must be setup
    # remote must also have develop branch

def commit(explicit=False):
    # if something is to commit, ask for message can be free if there are
    # already other commits, must be guideline conform if its the first

    # todo: tell user the user something like git status and ask what he wants to do
    # todo: if untracked files, add them
    # todo: inform user that now with DVCS, he could check in locally. But dont do it
    #       if he changed only a few files, or if preferences turn off that msg.
    repo = git.repo()
    has_changes = repo.has_local_changes()
    allow_empty = False
    if not has_changes and explicit:
        msg = "You don't have any local changes to commit. " +\
            "Do you want to force creating an empty commit?"
        if tkMessageBox.askokcancel("whatever",msg)==0:
            raise Exception("Aborted by User")
        allow_empty = True
        
    if has_changes or allow_empty:
        if is_nice_branch():
            if explicit:
                pre_msg = "You"
            else:
                pre_msg = "You have local changes which need to be commited first. But you"
            msg = pre_msg + " are on currently on a nice branch (" + nice_branch + "). " +\
                  "Normally you want commit to the free branch (" + ugly_branch + ") " +\
                  "and then use 'make branch nice'. " +\
                  "Continue committing to the nice branch?"
            if tkMessageBox.askyesno("whatever", msg)==0:
                raise Exception("Aborted by user")
        elif not explicit:
            msg = "You have local changes which need to be commited first. I will commit them now."
            if tkMessageBox.askokcancel("whatever", msg)==0:
                raise Exception("Aborted by user")
        repo.commit(allow_empty)

def make_branch_nice():
    # goal must be that in central repo only nice commits apear in non
    # private/feature branches
    #
    # !!!!!!!!!! that does mean we cant merge private feature branches into
    # develop, because after the merge it is unknown which of the parents belong
    # to the old feature and which to the old developper branch

    # test that default_origin_branch is a descedant of default_branch so no
    # merge conflicts are possible

    # - also check that the commit im going to push only has parents already on
    # - central repo, i.e. dont introduce unchecked commits into central repo

    # if current branch has not origin/working as direct parent ask wheter to
    # really do it - the user might want to merge the new origin/working into
    # the current branch first

    # a feature-nice branch which 'mirrors' the featur branch: - dont merge into
    # origin/working (so the central has linear history) its not possible to
    # have a 'nice-' branch, becaouse only single commits which are not merge
    # commits can be pushed to the central repo. You only get that with
    # rebasing. And you don't want to insert the commits at the beginning of the
    # nice branch multiple times into the central repo.


    # git checkout (wo feature von origin/working wegbranchts [aka letzer pull merge])
    # git merge --squash --ff-only feature
    # git commit (runs check hooks) -a -m guide-line-conforming-msg
    # tag feature commit as 'feature-niced-23' and in tag comment date & time
    # (git push)

    # abort if working tree not clean
    # working_changes = subprocess.call([git_binary,"diff","--exit-code"])
    # index_changes = subprocess.call([git_binary,"diff","--cached","--exit-code"])
    # if working_changes:
    #     raise Exception("working tree not clean")
    # if index_changes:
    #     raise Exception("index (aka staging area) not clean")

    # abort if branch is already nice 
    
    # origin_branch = "remotes/origin/master"
    #base_commit = subprocess.check_output([git_binary,"merge-base",origin_branch,ugly_branch])

    repo = git.repo()
    if is_nice_branch():
        if repo.has_local_changes():
            msg = "You are already on the nice branch (" + nice_branch + ") and you " +\
                "you have local changes which a) you normally don't want to commit to " +\
                "the nice branch and which b) prevents me from automatically switching " +\
                "to the free branch (" + ugly_branch + "). Aborting."
            tkMessageBox.showinfo("whatever", msg )
            raise Exception("Aborted")
        else:    
            msg = "You are already on the nice branch (" + nice_branch + "). " +\
                "I will switch to free branch (" + ugly_branch + ") first."
            if tkMessageBox.askokcancel("whatever", msg )==0:
                raise Exception("Aborted by user")
            repo.checkout(ugly_branch)
            
    commit()
    if repo.has_diffs(ugly_branch,nice_branch):
        repo.checkout(nice_branch)
        repo.merge_squash(ugly_branch)

        tkMessageBox.showinfo("whatever", "Making-nice was successfull. Will now commit the new nice commit.")
        repo.commit()
        # todo: if the user commits stuff on the nice branch directly and later makes nice
        # he has merge conflicts everytime he runs make nice

        # that helps to see which commit of ugly_branch was already merged into
        # nice-branch. But it also makes rebasing nice-branch to a new remote
        # branch 'impossible'
        # repo.checkout(ugly_branch)
        # repo.merge(nice_branch)

        # at the end ugly_branch is checkedout, so one can continue working on
        # it right away

def unique_branch_name(base_name):
    """Returns a uniq branch name which starts with the given base"""
    branches = git.repo().branches()
    collision = True
    count = 1
    while collision:
        new_branch = base_name + "-bak-" +str(count)
        collision = next((x for x in branches if x == new_branch), False)
        count += 1
    return new_branch

def fetch_rebase():
    # todo: clone if not already exists. however, wasnt that done upon registering?
    # ???? use --rebase?o
    if subprocess.call([git_binary,"fetch"]):
        raise Exception("git fetch failed")
    if subprocess.call([git_binary,"rebase",default_origin_branch]):
        raise Exception("git rebase failed")

def ask_message():
    return "hello"

def is_nice_branch():
    return re.search( nice_branch_regex, git.repo().current_branch() )


# git hooks
# =========

# see man page githooks(5)
def pre_commit_hook():
    if is_nice_branch():
      print "git-dragon: a nice branch, checking commit. nice_branch_regex = '" + nice_branch_regex + "'"
    else:
      print "git-dragon: not a nice branch, not doing anything. nice_branch_regex = '" + nice_branch_regex + "'"
    return 0

# see man page githooks(5)
def prepare_commit_msg_hook(args):
    # assume that we are in a commit run with --no-verify. commit_msg_hook will replace it
    # with the correct one in the no --no-verify case
    if is_nice_branch():
        filename = args[0]
        msg_src = args[1] if len(args)>=1 else None
        f = open(filename, 'r+')
        msg = f.read()

        msg = help_msg + re.sub(r'(?m)^#.*$',"",msg) + '\n' + no_verify_sign_off_str
        # todo: when user commits with --no-verify, automatically
        # insert the reason here (maybe its better to not support that
        # convenience. We want to make it cumbersome to commit without verify).

        f.seek(0)
        f.truncate()
        f.write(msg) 
        f.close()
    return 0

# see man page githooks(5)
# pre-commit hook approved commit, so the commit can be signed-off as being ok
# --signoff option to git is not used so it is easier to work with arbitry
# front-ends not provding/offering the --signoff option
def commit_msg_hook(filename):
    if is_nice_branch():
        print "git-dragon: checks passed. signing off commit"
        f = open(filename, 'r+')
        msg = f.read()

        # todo: first test that when user wants to commit with
        # gitconnector-no-verify he gives a reason
        msg = re.sub( re.escape(no_verify_sign_off_str) , "", msg )

        msg += '\n' + sign_off_str
        f.seek(0)
        f.truncate()
        f.write(msg) 
        f.close() 
    return 0

# see man page githooks(5)
def update_hook(ref_name,old_obj,new_obj):
    msg = git.commit(new_obj).message()
    regex = r'^' + re.escape(sign_off_str) + r'|^' + re.escape(no_verify_sign_off_str)
    if re.search( regex, msg, re.M ):
        print "git-dragon(remote): accepting commit " + new_obj
        return 0
    else:
        print "git-dragon(remote): refusing non-signed-off commit " + new_obj
        print msg
        print "---------"
        return 1

