#!/usr/bin/python
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

    def checkout(self,treeish):
        if not self.current_branch()==treeish:
            if subprocess.call([git_binary,"checkout",treeish]):
                raise Exception("git checkout failed")
        
    def merge_squash(self,treeish):
        if subprocess.call([git_binary,"merge","--squash","--ff-only",treeish]):
            raise Exception("git merge --squash failed") 
        if subprocess.call([git_binary,"commit","-a"]): 
            raise Exception("git merge --squash failed") 
        print "hello"

    def push(self):
        if subprocess.call([git_binary,"push"]):
            raise Exception("git push failed")

    def pull(self):
        # todo: clone if not already exists. however, wasnt that done upon registering?
        # flag 'rewrite-local-commits' decides wheter --rebase is allowed
        if subprocess.call([git_binary,"pull","--rebase"]):
            raise Exception("git pull failed")


#class commit:    
