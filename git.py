#!/usr/bin/python 2.7

# A wrapper around git (i.e. the git binary). Should be replaced by an existing
# API binding. See for example
# http://stackoverflow.com/questions/4034962/which-language-has-the-best-git-api-bindings.
#
# Promising solutions:
# - Using pygit2 (https://github.com/libgit2/pygit2) seems promising, because the underlying 
#   libgit2 (http://libgit2.github.com/) seems to be a stable API. TortoiseGit also seems to
#   use libgit2.
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


# See file README for what gitconnector is

import subprocess
import re
import os
import string

git_binary = "/usr/bin/git"

def is_repo(path):
    # cwd = os.getcwd()
    # isrepo = True
    # try:
    #     os.chdir(path)
    #     git.repo().get_status()
    # except Exception as e:
    #     isrepo = False
    # os.chdir(cwd)
    if path[-1]!="/":
        path += "/"
    return os.path.exists(path + ".git") or \
        (os.path.exists(path + "HEAD") and os.path.exists(path + "refs"))
        

class commit:
    sha1 = 0

    def __init__(self,sha1):
        self.sha1 = sha1

    def message(self):
        """Returns body of commit message"""
        ref_exp = self.sha1 + "^.." + self.sha1
        return subprocess.check_output([git_binary,"log","--pretty=format:%b", ref_exp])

class cmd:
    @staticmethod
    def call(args,raise_exception=True):
        args = [git_binary] + args
        print string.join(args)
        po = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        stdout = po.communicate()[0]
        if raise_exception and po.returncode:
            raise Exception( stdout )
        return po.returncode, stdout

class repo:    
    def git_dir(self):
        """Returns the path of the base of the repository, typically '.git/'"""
        # todo: use os.path & co
        if 'GIT_DIR' in os.environ:
            tmp = os.environ['GIT_DIR']
            if not tmp.endswith('/'):
                tmp += '/'
            return tmp
        else:
            return '.git/'

    def branches(self):
        """Returns local refs/heads (i.e. actually not really branch names)"""
        sha_and_ref = subprocess.check_output([git_binary,"show-ref"]).splitlines()
        ro = re.compile(r'^[^ \t]+[ \t]+(refs/heads/.+)$')
        return [ro.match(x).group(1) for x in sha_and_ref if ro.match(x)]

    def current_branch(self,str_if_none=False):
        """Returns current branch's name (actually not a branch name but a ref).
        If you're on a detached HEAD, None is returned if str_if_none is False,
        else the string '(no branch)' is returned."""
        raw_branches = subprocess.check_output([git_binary,"branch"]).splitlines()
        ro = re.compile(r'^\* (.*)$')
        for x in raw_branches:
            mo = ro.match( x )
            if mo:
                branch = mo.group(1)
                ref = "refs/heads/" + branch
                if mo and re.match( r'^\(', branch ):
                    if str_if_none:
                        return ref
                    else:
                        return None
                elif mo:
                    return ref
        return None

    def has_branch(self,ref):
        if not re.match(r'^refs/heads/',ref):
            ref = "refs/heads/" + ref
        return next((x for x in self.branches() if x==ref), False)

    def head(self):
        return 

    def create_branch(self,ref,startpoint="HEAD"):
        """Create a new branch with the name REF (given as ref, not as branch name)"""
        branch = re.sub( r'^refs/heads/', "", ref )
        if subprocess.call([git_binary,"branch", branch, startpoint]):
            raise Exception("git branch failed")

    def delete_branch(self,ref,force=False):
        branch = re.sub( r'^refs/heads/', "", ref )
        if subprocess.call([git_binary,"branch", "-D" if force else "-d", branch]):
            raise Exception("git branch -d failed")
        
    # todo: move to commit class
    def t1containst2(self,treeish1,treeish2):
        """Returns true if treeish1 contains treeish2. I.e. if treeish2 is an
        anchestor of or equal to treeish2"""
        rev_exp = treeish1 + ".." + treeish2
        tmp = subprocess.check_output([git_binary,"rev-list","-n",str(1),rev_exp]).splitlines()
        return len(tmp)==0

    # todo: move to commit class
    def get_sha1(self,treeish):
        return subprocess.check_output([git_binary,"rev-list","-n",str(1),treeish]).rstrip()

    def has_diffs(self, treeish1, treeish2 ):
        return subprocess.call([git_binary,"diff", "--exit-code", treeish1, treeish2])

    def has_local_changes(self):
        return subprocess.call([git_binary,"diff", "--exit-code"]) or \
            subprocess.call([git_binary,"diff", "--exit-code", "--cached"])

    def checkout(self,treeish):
        # if treeish is not a branch name, we'll be in detached head. So convert treeish
        # to branch name if possible. A branch name is a name that, when prepended with
        # "refs/heads/", is a valid ref (see git-commit, <branch> option)
        treeish = re.sub( r'^refs/heads/', "", treeish )
        if subprocess.call([git_binary,"checkout",treeish]):
            raise Exception("git checkout failed")
        
    def merge_squash(self,treeish):
        # --no-stat: not needed, and takes a 'long' time (relative to the actual merge).
        (exitcode,stdout) = cmd.call(["merge","--squash","--no-commit","--no-stat",treeish],raise_exception=False)
        if exitcode:
            if self.get_status2() & self.MERGE:
                raise Exception("Automatic squash merge failed. You have to manually fix merge conflicts.")
            else:
                raise Exception(stdout)

    def commit(self,allow_empty=False,commit_msg=None):
        cmd = [git_binary,"commit","-a"]
        if allow_empty:
            cmd.append("--allow-empty")
        if commit_msg:
            cmd.extend(["-m",commit_msg,"--edit"])
        if subprocess.call(cmd):
            raise Exception("git commit failed") 

    def merge_base(self,treeish1,treeish2):
        # todo: make shure the order of 1 2 is correct
        return subprocess.check_output([git_binary,"merge-base",treeish1,treeish2]).rstrip()

    def parent_branch(self,treeish,parents=None):
        # todo: finds the branch the treeish is branched off from
        return

    def merge(self,treeish):
        # --no-stat: not needed, and takes a 'long' time (relative to the actual merge).
        cmd.call(["merge","--commit","--no-stat",treeish])

    def merge_abort(self):
        if subprocess.call([git_binary,"reset","--merge"]):
            raise Exception("git merge failed") 

    def rebase(self,treeish):
        if subprocess.call([git_binary,"rebase","--no-stat",treeish]):
            raise Exception("git rebase failed") 

    def rebase_continue(self):
        if subprocess.call([git_binary,"rebase","--continue"]):
            raise Exception("git rebase failed") 

    def rebase_abort(self):
        if subprocess.call([git_binary,"rebase","--abort"]):
            raise Exception("git rebase failed") 

    def am_abort(self):
        if subprocess.call([git_binary,"am","--abort"]):
            raise Exception("git am failed") 

    def bisect_abort(self):
        if subprocess.call([git_binary,"bisect","reset"]):
            raise Exception("git bisect failed") 
    
    def push(self,remote=None,refspec=None):
        cmd = [git_binary,"push"]
        if not remote:
            remote = "origin"
        cmd.append(remote)
        if not refspec:
            refspec = "master-nice:master"
        cmd.append(refspec)
        print cmd
        if subprocess.call(cmd):
            raise Exception("git push failed")

    def reset(self,treeish,mode):
        if subprocess.call([git_binary,"reset","--" + mode,treeish]):
            raise Exception("git reset failed")

    def fetch(self,remote=None,refspec=None):
        # The defaults make sure that a misconfigured config file does not
        # influence gitconnector.
        # Always fetching all refs is not as efficient as it could be, but its
        # git's default and its easy, simple. Only getting what is needed is more
        # error prone, confusing
        cmd = [git_binary,"fetch"]
        if not remote:
            remote = "origin"
        cmd.append(remote)
        if not refspec:
            refspec = "+refs/heads/*:refs/remotes/origin/*"
        cmd.append(refspec)
        print cmd
        if subprocess.call(cmd):
            raise Exception("git fetch failed")

    def pull(self,remote,refspec):
        # todo: clone if not already exists. however, wasnt that done upon registering?
        # flag 'rewrite-local-commits' decides wheter --rebase is allowed
        if subprocess.call([git_binary,"pull",remote, refspec]):
            raise Exception("git pull failed")

    def commits_ahead(self,a,b):
        # todo: cache
        log = subprocess.check_output([git_binary,"log","--oneline",a+".."+b]).splitlines()
        if len(log)==0:
            return 0
        else:
            return len(log.splitlines())

    def get_status(self):
        return subprocess.check_output([git_binary,"status"])

    NORMAL = 0
    MERGE = 1 # including squash merge
    REBASE = 2
    APPLY_MAILBOX = 4
    BISECT = 8

    def get_status2(self):
        git_dir = self.git_dir()
        status = self.NORMAL
        # I don't know which can co-exist and which are mutually exclusive. I
        # assume only bisect can coexist with others
        if os.path.exists( os.path.join(git_dir,"rebase-apply/applying") ):
            status = status | self.APPLY_MAILBOX
        elif os.path.exists( os.path.join(git_dir, "rebase-apply") ) or \
             os.path.exists( os.path.join(git_dir, "rebase-merge") ) :
            status = status | self.REBASE
        elif os.path.exists( os.path.join(git_dir, "MERGE_HEAD") ) or \
             os.path.exists( os.path.join(git_dir, "SQUASH_MSG") ):
            status = status | self.MERGE
        if os.path.exists( os.path.join(git_dir,"BISECT_START") ):
            status = status | self.BISECT
        return status   

    def is_reachable(self,ref):
        # todo: cache
        # output: sha1<SP>fully-qualified-ref<NL>
        all_refs = subprocess.check_output([git_binary,"show-ref","--heads","--tags"]).splitlines()
        ro = re.compile(r'[^ ]+ +' + re.escape(ref) + r'$')
        all_refs_but_x = filter( lambda r: not ro.match(r), all_refs )
        ro = re.compile(r'([^ ]+)')
        all_shas_but_x = map( lambda r: ro.match(r).group(1), all_refs_but_x )
        tmp = subprocess.check_output([git_binary,"log", ref, "--not"] + all_shas_but_x).splitlines()
        return len(tmp)==0

    def cut_parent_count(self,treeish,count):
        "Returns min of 1) count 2) the number of first parents of treeish, o"

    def get_rev_range(self,start_treeish,end_treeish,count):
        """Return a revision range starting (incl.) at the count'th parent of
        start_treeish and ends (incl) end_treeish."""

        # todo: cache

        # + 1 because one line is the start_treeish itself
        # + another 1 because we want to see if there would be more 
        cmd = [git_binary,"rev-list","--first-parent","-n",str(count+2),start_treeish]
        refs = subprocess.check_output( cmd ).splitlines()
        # -1 becaue refs contain the treeish itself
        parent_cnt = len(refs)-1
        # smaller-EQUAL because the ".." in the else clause does never work for
        # cases where I want to start at the first commit
        if parent_cnt<=count:
            return end_treeish
        else:
            return start_treeish + "~" + str(count+1) + ".." + end_treeish

    def get_log_graph(self,remote,nice,free,context):
        """Returns an ascii log graph containing remote, nice and free and the
        context'th parent of the older merge base."""
        refs = []
        if remote and nice:
            base_nice = self.merge_base(remote,nice)
            refs.append( self.get_rev_range( base_nice, remote, context ) )
            refs.append( self.get_rev_range( base_nice, nice, context ) )
        if remote and free:
            base_free = self.merge_base(remote,free)
            refs.append( self.get_rev_range( base_free, remote, context ) )
            refs.append( self.get_rev_range( base_free, free, context ) )
        if remote and not refs:
            base_head = self.merge_base(remote,"HEAD")
            refs.append( self.get_rev_range( base_head, remote, context ) )
            refs.append( self.get_rev_range( base_head, "HEAD", context ) )
        if not refs:
            refs.append( self.get_rev_range( "HEAD", "HEAD", context ) )
        # todo: make more error prone: what if free is older, or if there are
        # not more commits todo: maybe 'show-branch --merge-base' or merge-base
        # can be used to find the 'oldest' common anchestor from which we want
        # or use 'branch (--merged | --no-merged | --contains)' ??

        # to go context commits back
        # todo: also give context on 'top' of graph
        if not refs:
            return ""
        else:
            cmd = [git_binary,"log", "--graph", "--oneline", "--first-parent", "--decorate=short"]
            cmd.extend(refs)
            return subprocess.check_output( cmd )

#class commit:    
