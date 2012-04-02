#!/usr/bin/python 2.7
import subprocess
import re
import os


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

class repo:    
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

    def create_branch(self,name,startpoint="HEAD"):
        if subprocess.call([git_binary,"branch", name, startpoint]):
            raise Exception("git branch failed")

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
        if subprocess.call([git_binary,"merge","--squash",treeish]):
            raise Exception("git merge --squash failed") 

    def commit(self,allow_empty=False):
        if allow_empty:
            if subprocess.call([git_binary,"commit","-a","--allow-empty"]):
                raise Exception("git commit failed") 
        else:
            if subprocess.call([git_binary,"commit","-a"]):
                raise Exception("git commit failed") 

    def merge_base(self,treeish1,treeish2):
        return subprocess.check_output([git_binary,"merge-base",treeish1,treeish2]).rstrip()

    def merge(self,treeish):
        if subprocess.call([git_binary,"merge","--commit",treeish]):
            raise Exception("git merge failed") 

    def rebase(self,treeish):
        if subprocess.call([git_binary,"rebase",treeish]):
            raise Exception("git rebase failed") 

    def push(self,treeish):
        if subprocess.call([git_binary,"push","origin",treeish + ":master"]):
            raise Exception("git push failed")

    def reset(self,treeish,mode):
        if subprocess.call([git_binary,"reset","--" + mode,treeish]):
            raise Exception("git reset failed")

    def pull(self):
        # todo: clone if not already exists. however, wasnt that done upon registering?
        # flag 'rewrite-local-commits' decides wheter --rebase is allowed
       if subprocess.call([git_binary,"pull"]):
            raise Exception("git pull failed")

    def commits_ahead(self,a,b):
        log = subprocess.check_output([git_binary,"log","--oneline",a+".."+b]).splitlines()
        if len(log)==0:
            return 0
        else:
            return len(log.splitlines())

    def get_status(self):
        return subprocess.check_output([git_binary,"status"])

    def is_reachable(self,refx):
        # all_refs = subprocess.check_output([git_binary,"show-ref","--heads","--tags"]).splitlines()
        # ro = re.compile(r'[^ ]+ +' + re.escape(branch) + r'$')
        # all_refs_but_x = filter( lambda r: not ro.match(r), all_refs )
        # ro = re.compile(r'([^ ]+)')
        # all_shas_but_x = map( lambda r: ro.match(r).group(1), all_refs_but_x )
        # tmp = subprocess.check_output([git_binary,"log", refx, "--not"].append(all_shas_but_x)).splitlines()
        # return len(tmp)==0
        return True

    def cut_parent_count(self,treeish,count):
        "Returns min of 1) count 2) the number of first parents of treeish, o"

    def get_rev_range(self,start_treeish,end_treeish,count):
        """Return a revision range starting (incl.) at the count'th parent of
        start_treeish and ends (incl) end_treeish."""
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
        # not more commits
        if not refs:
            return ""
        else:
            tmp = [git_binary,"log", "--graph", "--oneline", "--decorate=short"]
            tmp.extend(refs)
            return subprocess.check_output( tmp )

#class commit:    
