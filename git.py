#!/usr/bin/python 2.7
import subprocess
import re


git_binary = "/usr/bin/git"

class git_cmd:    
    def foo(self,args):
        return
        
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
        """Returns branch names. The current branch is the first"""
        raw_branches = subprocess.check_output([git_binary,"branch"]).splitlines()
        branches = []
        current_cnt = 0
        for raw_branch in raw_branches:
            if re.match(r'\*', raw_branch ):
                branches.insert(0,raw_branch[2:])
                current_cnt += 1
            else:    
                branches.append(raw_branch[2:])
        if len(branches)==0 or current_cnt!=1:
            raise Exception("No branches found or multiple current branches")
        return branches

    def current_branch(self):
        """Returns current branch's name"""
        return self.branches()[0]

    def make_branch(self,name):
        if subprocess.call([git_binary,"branch", name]):
            raise Exception("git branch failed")

    def has_diffs(self, treeish1, treeish2 ):
        return subprocess.call([git_binary,"diff", "--exit-code", treeish1, treeish2])

    def has_local_changes(self):
        return subprocess.call([git_binary,"diff", "--exit-code"]) or \
            subprocess.call([git_binary,"diff", "--exit-code", "--cached"])

    def checkout(self,treeish):
        if not self.current_branch()==treeish:
            if subprocess.call([git_binary,"checkout",treeish]):
                raise Exception("git checkout failed")
        
    def merge_squash(self,treeish):
        if subprocess.call([git_binary,"merge","--squash",treeish]):
            raise Exception("git merge --squash failed") 

    def commit(self,allow_empty):
        if allow_empty:
            if subprocess.call([git_binary,"commit","-a","--allow-empty"]):
                raise Exception("git commit failed") 
        else:
            if subprocess.call([git_binary,"commit","-a"]):
                raise Exception("git commit failed") 

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

    def get_status(self):
        return subprocess.Popen([git_binary,"status"],stdout=subprocess.PIPE).communicate()[0]

    def get_log_graph(self,remote,nice,free):
        base_nice = subprocess.Popen([git_binary,"merge-base",remote,nice],stdout=subprocess.PIPE).communicate()[0].rstrip()
        base_free = subprocess.Popen([git_binary,"merge-base",remote,free],stdout=subprocess.PIPE).communicate()[0].rstrip()
        # todo: make more error prone: what if free is older, or if there are not more commits
        return subprocess.Popen([git_binary,"log", "--graph", "--oneline","--decorate=short",\
                                 base_nice + "^^.." + nice,\
                                 base_free + "^^.." + free,\
                                 base_nice + "^^.." + remote,\
                                 base_free + "^^.." + remote \
                                     ],stdout=subprocess.PIPE).communicate()[0]


#class commit:    
