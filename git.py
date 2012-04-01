#!/usr/bin/python 2.7
import subprocess
import re


git_binary = "/usr/bin/git"

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

    def get_log_graph(self,remote,nice,free):
        refs = []
        if remote and nice:
            base_nice = self.merge_base(remote,nice)
            refs.append(base_nice + "~2.." + remote)
            refs.append(base_nice + "~2.." + nice)
        if remote and free:
            base_free = self.merge_base(remote,free)
            refs.append(base_free + "~2.." + free)
            refs.append(base_free + "~2.." + free)
        # todo: make more error prone: what if free is older, or if there are
        # not more commits
        print refs    
        if not refs:
            return ""
        else:
            tmp = [git_binary,"log", "--graph", "--oneline", "--decorate=short"]
            tmp.extend(refs)
            return subprocess.check_output( tmp )

#class commit:    
