#!/usr/bin/python
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

git_binary = "/usr/bin/git"
default_branch = "master"
default_origin_branch = "remotes/origin/master"
nice_branch_regex = r'.*-nice$' 
sign_off_str = "Signed-off-by: git-dragon"
no_verify_sign_off_str = "Signed-off-by: git-dragon no-verify"

def check_push_guidelines():
    check_content()
    check_buildable()
    check_test_suite_runs()
    check_message("foo")

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

def commit_locally():
    # if something is to commit, ask for message can be free if there are
    # already other commits, must be guideline conform if its the first

    # todo: if untracked files, add them
    # todo: if no changes whatsoever abort
    # todo: inform user that now with DVCS, he could check in locally. But dont do it
    #       if he changed only a few files, or if preferences turn off that msg.
    working_changes = subprocess.call([git_binary,"diff","--exit-code"])
    index_changes = subprocess.call([git_binary,"diff","--cached","--exit-code"])
    if working_changes or index_changes:
        if working_changes:
            print "working tree canges, will locally comit"
        if index_changes:
            print "index canges, will locally comit"
        if subprocess.call([git_binary,"commit","-a"]):
            raise Exception("git commit failed")
    else:
        print "working tree and index clean, no local commit needed"

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
    # have a 'nice-' branch, because only single commits which are not merge
    # commits can be pushed to the central repo. You only get that with
    # rebasing. And you don't want to insert the commits at the beginning of the
    # nice branch multiple times into the central repo.


    # git checkout (wo feature von origin/working wegbranchts [aka letzer pull merge])
    # git merge --squash --ff-only feature
    # git commit (runs check hooks) -a -m guide-line-conforming-msg
    # tag feature commit as 'feature-niced-23' and in tag comment date & time
    # (git push)

    # abort if working tree not clean
    working_changes = subprocess.call([git_binary,"diff","--exit-code"])
    index_changes = subprocess.call([git_binary,"diff","--cached","--exit-code"])
    if working_changes:
        raise Exception("working tree not clean")
    if index_changes:
        raise Exception("index (aka staging area) not clean")

    # abort if branch is already nice 
    
    nice_branch = "master-nice"
    ugly_branch = "master-ugly"
    origin_branch = "remotes/origin/master"


    base_commit = subprocess.check_output([git_binary,"merge-base",origin_branch,ugly_branch])

    if subprocess.call([git_binary,"checkout",base_commit]):
        raise Exception("git checkout failed")
    if subprocess.call([git_binary,"merge","--squash","--ff-only",ugly_branch]):
        raise Exception("git merge failed") # what then?

    # for now let git ask the message
    if subprocess.call([git_binary,"commit","-a","-s"]):
        raise Exception("git commit failed")
    
def get_backup_branchname():
    branches = subprocess.check_output([git_binary,"branch"]).splitlines()
    # branches = map( branches, ) remove leading 2 chars
    collision = True
    count = 1
    while collision:
        new_branch = "geil" + str(count)
        collision = next((x for x in branches if x == ("  " + new_branch)), False)
        count += 1
    print "found new branch name " + new_branch    
    return new_branch

def pull():
    # todo: clone if not already exists. however, wasnt that done upon registering?
    # flag 'rewrite-local-commits' decides wheter --rebase is allowed
    if subprocess.call([git_binary,"pull","--rebase"]):
        raise Exception("git pull failed")

def fetch_rebase():
    # todo: clone if not already exists. however, wasnt that done upon registering?
    # ???? use --rebase?o
    if subprocess.call([git_binary,"fetch"]):
        raise Exception("git fetch failed")
    if subprocess.call([git_binary,"rebase",default_origin_branch]):
        raise Exception("git rebase failed")

def push():
    # first time I had to git push origin '*:*'
    if subprocess.call([git_binary,"push"]):
        raise Exception("git push failed")
    return False

def ask_message():
    return "hello"

def is_nice_branch():
    return re.search( nice_branch_regex, git.repo().current_branch() )


# 0 dont do anything
# 1 check and sign off
# 2 ask
config_locall_commit=0 

# see man page githooks(5), pre-commit
def pre_commit_hook():
    if is_nice_branch():
      print "git-dragon: a nice branch, checking commit. nice_branch_regex = '" + nice_branch_regex + "'"
    else:
      print "git-dragon: not a nice branch, not doing anything. nice_branch_regex = '" + nice_branch_regex + "'"
    return 0

def prepare_commit_msg_hook(args):
    # assume that we are in a commit run with --no-verify. commit_msg_hook will replace it
    # with the correct one in the no --no-verify case
    if is_nice_branch():
        filename = args[0]
        msg_src = args[1] if len(args)>=1 else None
        f = open(filename, 'a')
        f.write('\n' + no_verify_sign_off_str) 
        f.close()
    return 0

# see man page githooks(5), commit-msg
# pre-commit hook approved commit, so the commit can be signed-off as being ok
# --signoff option to git is not used so it is easier to work with arbitry
# front-ends not provding/offering the --signoff option
def commit_msg_hook(filename):
    if is_nice_branch():
        print "git-dragon: checks passed. signing off commit"
        f = open(filename, 'r+')
        msg = f.read()
        msg = re.sub( re.escape(no_verify_sign_off_str) , "", msg )
        msg += '\n' + sign_off_str
        f.seek(0)
        f.truncate()
        f.write(msg) 
        f.close() 
    return 0

# see man page githooks(5), pre-receive
def update_hook(ref_name,old_obj,new_obj):
    msg = git.commit(new_obj).message()
    regex = r'^' + re.escape(sign_off_str) + r'|^' + re.escape(no_verify_sign_off_str)
    if re.search( regex, msg, re.M ):
        print "git-dragon(remote): accepting commit " + new_obj
        return 0
    else:
        print "git-dragon(remote): refusing non-signed-off commit " + new_obj
        return 1

def release():
    check_environment()
    commit_locally()
    remote_has_changes = True # start with this assumption
    while remote_has_changes:
        pull() 
        make_branch_nice()          # switches from ugly to nice branch
        remote_has_changes = push() # set remote_has_changes
