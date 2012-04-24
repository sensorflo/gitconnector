#!/usr/bin/python2.7
# Core functionality 
# See file README for info what gitconnector is
#
# Copyright 2012 Florian Kaufmann <sensorflo@gmail.com>
# 
# This work is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or any later version.
# 
# This work is distributed in the hope that it will be useful, but without any
# warranty; without even the implied warranty of merchantability or fitness for
# a particular purpose. See version 2 and version 3 of the GNU General Public
# License for more details. You should have received a copy of the GNU General
# Public License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

import re
import git
import tkMessageBox

# technically these are refs, not branch names. branch names are only what can
# come after refs/head
default_nice_branch = "refs/heads/master-nice" 
default_free_branch = "refs/heads/master"
default_remote_branch = "refs/remotes/origin/master" # todo: rename to remote tracking branch??
# the same string 'git branch' uses. Is not required, but is more
# consistent
no_branch = "(no branch)"
# todo: customizeable fetch/push refspec, merge/rebase options for nice/free
#       dont use gits


RESET_FREE_WITH_BAK = 0
RESET_FREE_NO_BAK = 1
DELETE_FREE = 2      # After push, after asking, free is deleted
CONTINUE_ON_FREE = 3 # changes to remote branch are always merged into free
free_branch_cleanup = CONTINUE_ON_FREE
delete_nice_after_push = True

# If a branch matches it is a nice branch, else it is a free branch. To convert
# a nice branch name into an free branch name, the matching group 1 is removed
nice_branch_regex = r'(-nice)$' 

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


def version():
    return "0.2"

# should probable be name get_branch_name or the like?
def abbrev_ref(ref):
    return re.sub( r'^refs/(remotes/|heads/)?', "", ref)

def free_branch(allow_create=False, str_if_none=False):
    """Returns the free branch associated with the current branch."""
    repo = git.repo()
    current_branch = repo.current_branch()
    result = None
    if current_branch:
        if not is_nice_branch(current_branch):
            result = current_branch
        else:
            proposed_branch = re.sub( nice_branch_regex, "", current_branch)
            if not repo.has_branch(proposed_branch):
                if allow_create:
                    result = proposed_branch
                    repo.create_branch(proposed_branch,startpoint=remote_branch())
            else:
                result = proposed_branch
    if not result and str_if_none:
        result = no_branch
    return result

def nice_branch(allow_create=False, str_if_none=False):
    """Analogous to free_branch"""
    repo = git.repo()
    current_branch = repo.current_branch()
    result = None
    if current_branch:
        if is_nice_branch(current_branch):
            result = current_branch
        else:
            proposed_branch = current_branch + "-nice"
            if not repo.has_branch(proposed_branch):
                if allow_create:
                    result = proposed_branch
                    repo.create_branch(proposed_branch,startpoint=remote_branch())
            else:
                result = proposed_branch
    if not result and str_if_none:
        result = no_branch
    return result


def remote_branch(str_if_none=True):
    return default_remote_branch

def check_detached_head():
    if not git.repo().current_branch():
        msg = "You have no branch checked out, i.e. you're in a detached head state. " +\
            "You need need to check out a branch first. Aborting."
        tkMessageBox.showerror("", msg )
        raise Exception("Aborted")

def publish(explicit=False):
    repo = git.repo()
    # has_local_changes = repo.has_local_changes()
    # ahead = (repo.commits_ahead(repo.current_branch(),remote_branch)!=0)
    # is_alreay_nice = False

    check_detached_head()

    saved_current_branch = repo.current_branch()
    
    # nothing to do
    # if not has_local_changes and not ahead:
    #     msg = "You neither have local changes nor have you made commits " +\
    #           "on your current branch (" + repo.current_branch() + ") relative " +\
    #           "to the remote tracking branch (" + remote_branch + "). Nothing to do."
    #     tkMessageBox.showinfo("", msg )
    #     raise Exception("Aborted");

    # directly commit to nice branch if possible / avoid committing to free
    # branch which will then have only one commit, which is stupid (but not an
    # error)
    # elif has_local_changes and not ahead:
    #     repo.checkout(nice_branch)
    #     commit(ask_when_nice=False)
    #     is_alreay_nice = True

    # 
    # elif has_local_changes:
    #     commit()
    commit()
    
    # pull before make_branch_nice, because after make_branch_nice we want have
    # low probability to have to merge again
    pull()
    make_branch_nice()

    nice = nice_branch() 
    if not nice:
        raise Exception("Internal error") # make_branch_nice should have created one
    # repo.checkout( nice ) # todo: is that really needed?
    repo.push( None, nice + ":master" ) # todo: how to make less explicit?
    
    free = free_branch() 
    if free:
        # remote has changed since nice was pushed into it -> merge those
        # commits into free. But only if we don't throw away the free branch anyway
        # todo: only call pull for free
        # todo: what happens if we got interrupted before (e.g. merge conflicts)?
        if not (free_branch_cleanup==DELETE_FREE or free_branch_cleanup==RESET_FREE_NO_BAK):
            repo.checkout(free)
            repo.merge(remote_branch())

        if free_branch_cleanup==RESET_FREE_WITH_BAK or free_branch_cleanup==RESET_FREE_NO_BAK:
            if free_branch_cleanup==RESET_FREE_WITH_BAK and not repo.is_reachable( free ):
                repo.create_branch( unique_branch_name( free ), free)
            # todo: if it is not the current branch, don't use checkout
            repo.checkout(free)    
            if not repo.has_local_changes():
                repo.reset(remote_branch(),"hard")
            else:
                raise Exception("Internal error")

        elif free_branch_cleanup==DELETE_FREE:
            repo.delete_branch(free,force=True)

        elif free_branch_cleanup==CONTINUE_ON_FREE:
            pass
        
        else:
            raise Exception("internal error")

        # free branch has changed -> update local variable 
        free = free_branch()

    if nice and delete_nice_after_push:
        # todo: only if the commit referenced by nice is referenced by something else
        #       however since we just pushed it into remote, that should always be the case
        # todo: first checkout free (hmm, is done above), or go into detached head
        free_sha1 = repo.get_sha1(free) if free else None
        nice_sha1 = repo.get_sha1(nice)
        if nice_sha1==free_sha1:
            repo.checkout(free)
        else:
            repo.checkout(nice_sha1)
        repo.delete_branch(nice)
        nice = None

    if explicit:
        if repo.has_branch(saved_current_branch):
            repo.checkout(saved_current_branch)
        elif free:
            repo.checkout(free)
        elif nice:
            repo.checkout(nice)
        # else: don't do anything, stay where we are


    # remote
    # _has_changes = True # start with this assumption
    # while remote_has_changes:
    #     pull() 
    #     make_branch_nice()          # switches from free to nice branch
    #     remote_has_changes = push() # set remote_has_changes

def pull(explicit=False):
    """Pulls from remote_branch. free_branch, if it exists, is merged.
    nice_branch, if it exists, is rebased."""
    repo = git.repo()
    check_detached_head()
    saved_current_branch = repo.current_branch()

    commit()
    remote = remote_branch() 

    # fetch. Dont use pull because we anyway have to local branches two deal
    # with: free and nice
    repo.fetch()

    # merge (updated) remote branch into free branch
    free = free_branch() 
    if free:
        repo.checkout(free)
        repo.merge(remote)

    # rebase nice branch onto (updated) remote branch
    # todo: what if the above pull fails? Then the nice_branch is not rebased which leads to troubles later
    # todo: should be done automatically within pull if nice-branch is setuped correctly
    nice = nice_branch() 
    if nice:
        repo.checkout(nice)
        repo.rebase(remote)

    if explicit:
        repo.checkout(saved_current_branch)


def get_status():
    # todo: emphasize when in merge/rebase conflict
    # todo: use same color for same branch names everywhere, also in graph log
    context = 2
    repo = git.repo()
    txt = ""
    status = repo.get_status2()
    
    # todo: most gitconnector commands should bark if status is not normal
    if status != repo.NORMAL:
        # todo: being in a rebase/am does not necessarily mean that we have merge 
        # conflicts. that need to be an extra flag
        txt += "!!! "
        if status & repo.REBASE:
            txt += "Within a rebase. "
        elif status & repo.APPLY_MAILBOX:
            txt += "Within an apply mailbox. "
        elif status & repo.MERGE:
            txt += "Within a merge. "
        if status & repo.BISECT:
            txt += "Within a bisect. "            
        txt += "(Menu Help/Sanitize has more info)"    
        txt += " !!!\n\n"
    txt += "--- current branch's friends ---\n"
    txt += "current branch         : " + abbrev_ref(repo.current_branch(str_if_none=True)) + "\n"
    txt += "free branch            : " + abbrev_ref(free_branch(str_if_none=True)) + "\n"   # x commits nice-able
    txt += "nice branch            : " + abbrev_ref(nice_branch(str_if_none=True)) + "\n"   # x commits pushable into remote
    txt += "remote tracking branch : " + abbrev_ref(remote_branch(str_if_none=True)) + "\n" # x commits ahead
    txt += "\n"
    txt += "log extract:\n"
    txt += repo.get_log_graph(remote_branch(),nice_branch(),free_branch(),context)
    # txt += "\nnice-able commits:\n"
    # txt += repo.
    # txt += "\npushable nice commits:\n"
    # txt += repo.

    # comes last because it can be arbitrarily long
    txt += "\n"
    txt += "--- status of index and working tree ---\n" 
    txt += repo.get_status()
    txt += "\n"
    txt += "\n"
    return txt, status

def abort(explicit=False):
    # maybe that button can be removed by putting its functionality into 'help (me out)'
    # or leave the abort button, and place the same functionality also in help me out
    repo = git.repo()
    status = repo.get_status2()
    if status == repo.NORMAL:
        tkMessageBox.showinfo("", "No merge, rebase, apply-mailbox, or bisect to abort.")
    else:    
        if tkMessageBox.askokcancel("Confirm abort","Aborting means you loose your changes to your working tree and your index. Working tree and index will be reset to the commit you started the merge/rebase with.")==0:
            raise Exception("Aborted by user")
        if status & repo.MERGE:
            repo.merge_abort()
        elif status & repo.REBASE:
            repo.rebase_abort()
        elif status & repo.APPLY_MAILBOX:
            repo.am_abort()
        elif status & repo.BISECT:
            repo.bisect_abort();
     

def sanitize(explicit=False):

    # - check_detached_head()
    # - if nice branch is current propose to switch to free branch
    # - give help if nice branch didn't pass the verification test during commit

    repo = git.repo()
    status = repo.get_status2()
    txt = ""
    title = ""
    if status == repo.NORMAL:
        if is_nice_branch( repo.current_branch() ):
            title = "current branch is the nice branch"
            txt = "Your current branch is the nice branch. Normally the current branch should be the free branch. "
            if not repo.has_local_changes():
                txt += "Shall I switch to the free branch?"
                if tkMessageBox.askyesno(title, txt )!=0:
                    repo.checkout(free_branch(allow_create=True))
                return # !!!!!!!!!!!!!!!!!!!!!
            else:
                txt += "Since you have changes to your working tree and/or index I can't offer to switch to the free branch. You first have either to commit your changes or reset them."
        else:    
            title = "Status normal"
            txt = "Currently everything seems normal, you don't need help. "
    else:    
        howto_resolve = \
          "or you resolved them but have not yet committed the result\n\n" +\
          "Use your favorite git front end (TortoiseGit, SmartGit, ...) to resolve the conflicts.\n\n"
        after_resolve1 = "After you resolved all conflicts press the "
        after_resolve2 = "Then you probably need to press again the button you started with in the beginning (e.g. relase, pull, ...).\n\n"
        if status & repo.REBASE:
            title = "MERGING WITHIN REBASING"
            txt += "A git rebase is running and you have to resolve manually merge conflicts,\n"
            txt += howto_resolve
            txt += after_resolve1 + 'continue rebase button. ' + after_resolve2
            txt += "If you are stuck, use abort button to abort the rebase.\n\n"
        elif status & repo.APPLY_MAILBOX:
            title = "MERGING WITHIN APPLING MAILBOX"
            txt += "A git am (apply mailbox) is running and you have to resolve manually merge conflicts,\n"
            txt += howto_resolve
            txt += after_resolve1 + 'continue am button. ' + after_resolve2
            txt += "If you are stuck, use abort button to abort the am.\n\n"
        elif status & repo.MERGE:
            title = "MERGING"
            txt += "You have merge conflicts which you need to resolve manually,\n"
            txt += howto_resolve
            txt += after_resolve1 + 'commit button. ' + after_resolve2
            txt += "If you are stuck, use abort button to abort the merge.\n\n"
        if status & repo.BISECT:
            title += " BISECTING"
            txt += "You are in the middle of a bisect. Use you're favorite git "
            txt += "frontend to continue or end the bisect."
            
    tkMessageBox.showinfo(title, txt )

def check_content():
    return

def check_test_suite_runs():
    return

def check_buildable():
    return

def check_message(message):
    return

def commit_or_continue(explicit=False):
    repo = git.repo()
    status = repo.get_status2()
    if status & repo.REBASE:
        repo.rebase_continue()
    elif status & repo.APPLY_MAILBOX:
        repo.am_continue()
    else: # inclues NORMAL, MERGE, BISECT
        commit(explicit)

def commit(explicit=False, ask_when_nice=True):
    # if something is to commit, ask for message can be free if there are
    # already other commits, must be guideline conform if its the first

    # todo: tell user the user something like git status and ask what he wants to do
    # todo: if untracked files, add them
    # todo: inform user that now with DVCS, he could check in locally. But dont do it
    #       if he changed only a few files, or if preferences turn off that msg.
    repo = git.repo()
    if explicit:
        check_detached_head()
        
    has_changes = repo.has_local_changes()
    allow_empty = False
    if not has_changes and explicit:
        msg = "You don't have any local changes to commit. " +\
            "Do you want to force creating an empty commit?"
        if tkMessageBox.askokcancel("",msg)==0:
            raise Exception("Aborted by User")
        allow_empty = True
        
    if has_changes or allow_empty:
        if is_nice_branch() and ask_when_nice:
            if explicit:
                pre_msg = "You"
            else:
                pre_msg = "You have local changes which need to be commited first. But you"
            nice = abbrev_ref(nice_branch(str_if_none=True))
            free = abbrev_ref(free_branch(str_if_none=True))
            msg = pre_msg + " are on currently on a nice branch (" + nice + "). " +\
                  "Normally you want commit to the free branch (" + free + ") " +\
                  "and then use 'make branch nice'. " +\
                  "Continue committing to the nice branch?"
            if tkMessageBox.askyesno("", msg)==0:
                raise Exception("Aborted by user")
        elif not explicit:
            msg = "You have local changes which need to be commited first. I will commit them now."
            if tkMessageBox.askokcancel("", msg)==0:
                raise Exception("Aborted by user")
        repo.commit(allow_empty)

def make_branch_nice(explicit=False):

    # if current branch has not origin/working as direct parent ask wheter to
    # really do it - the user might want to merge the new origin/working into
    # the current branch first

    # a feature-nice branch which 'mirrors' the featur branch: - dont merge into
    # origin/working (so the central has linear history) its not possible to
    # have a 'nice-' branch, becaouse only single commits which are not merge
    # commits can be pushed to the central repo. You only get that with
    # rebasing. And you don't want to insert the commits at the beginning of the
    # nice branch multiple times into the central repo.

    # todo: if the user commits stuff on the nice branch directly and later
    # makes nice he has merge conflicts everytime he runs make nice

    # idea: use default refspec, config & co
    # push free to nice not possible because that only works when it would be an
    # fast forward for nice
    # pull free from nice with --squash merge option probably possible, but pull default
    # should be so that it works fine for pulling from remote

    repo = git.repo()
    check_detached_head()
    saved_current_branch = repo.current_branch()

    # get free and nice branch and create as needed
    free = free_branch()
    nice = nice_branch(allow_create=True)
    remote = remote_branch()
    if nice and free:
        nice# nop
    elif nice and not free:
        if explicit:
            msg = "There is no free branch from which I could transfer commits to " +\
                "the current nice branch (" + abbrev_ref(nice) + "). Aborting."
            tkMessageBox.showinfo("", msg )
            raise Exception("Aborted")
        return
    elif not nice and free:
        nice = nice_branch( allow_create=repo.merge_base(free, remote ) )
    else:
        raise Exception("Internal error")
    abbrev_nice = abbrev_ref(nice)
    abbrev_free = abbrev_ref(free)
    abbrev_remote = abbrev_ref(remote)

    # 
    if not repo.t1containst2( nice, remote ):
        msg = "Nice branch ( " + abbrev_nice + ") is not a descendant (i.e. 'newer') of or equal to " +\
            "the remote branch (" + abbrev_remote +"). You have to pull first."
        tkMessageBox.showerror("", msg )
        raise Exception("Aborted")

    # commit local changes
    # However probably user dosn't want to commit to nice branch 
    if is_nice_branch():
        if repo.has_local_changes():
            msg = "You are on the nice branch (" + abbrev_nice + ") and you " +\
                "you have local changes which a) you normally don't want to commit to " +\
                "the nice branch and which b) prevents me from automatically switching " +\
                "to the free branch (" + abbrev_free + "). Aborting."
            tkMessageBox.showinfo("", msg )
            raise Exception("Aborted")
        elif explicit:
            msg = "You are on the nice branch (" + abbrev_nice + "). " +\
                "I will switch to free branch (" + abbrev_free + ") first."
            if tkMessageBox.askokcancel("", msg )==0:
                raise Exception("Aborted by user")
            repo.checkout(free)
    commit()

    # make-nice makes would be a no-op when nice branch's tip equals free's
    # branch tip
    has_diffs = repo.has_diffs(free,nice)
    if not has_diffs and explicit:
        msg = "Free branch (" + abbrev_free +") and nice branch (" + abbrev_nice + ")" +\
            "have no differences. Nothing todo."
        tkMessageBox.showinfo("", msg )
        raise Exception("Aborted")

    # actually do it
    elif has_diffs:
        repo.checkout(nice)
        repo.merge_squash(free)
        msg = "Making free branch nice was successfull. Will now commit the new nice commit."
        tkMessageBox.showinfo("Commiting", msg)
        repo.commit(commit_msg=help_msg)

    if explicit:
        repo.checkout(saved_current_branch)


def unique_branch_name(base_name):
    """Returns a uniq branch name which starts with the given base"""
    repo = git.repo()
    branches = repo.branches()
    collision = True
    count = 1
    while collision:
        new_branch = base_name + "-bak-" +str(count)
        collision = next((x for x in branches if x == new_branch), False)
        count += 1
    return new_branch

def ask_message():
    return "hello"

def is_nice_branch(branch=None):
    if not branch:
        branch = git.repo().current_branch()
    if branch:
        return re.search( nice_branch_regex, branch )
    else:
        return False

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
        f = open(filename, 'r+')
        msg = f.read()

        msg +=  '\n' + no_verify_sign_off_str
        # msg = help_msg + re.sub(r'(?m)^#.*$',"",msg) + '\n' + no_verify_sign_off_str
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
        # check conformoty of msg:
        # - brief 'line' contains no newlines (any style)

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

