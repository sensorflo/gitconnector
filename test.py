#!/usr/bin/python2.7
import unittest
import subprocess
import gitdragon

class TestGitConnector(unittest.TestCase):
    def setUp(self):
        subprocess.call(
            ["sh", "-c", 
            "rm -rf repos; " +\
            "mkdir -p repos/remote;" +\
            "git init repos/remote;" +\
            "git clone repos/remote repos/local1;" +\
            "git clone repos/remote repos/local2;"])

    def test_release(self):
        
        release()
        return

if __name__ == '__main__':
    unittest.main()    

# tests by hand
# 
# on nice branch
# echo foo >> main.cpp && git commit -a -m message --no-verify
# git log
# 
# on nice branch
# echo foo >> main.cpp && git commit -a -m message 
# git log
# 
# on non-nice branch
# echo foo >> main.cpp && git commit -a -m message 
# git log
# 
# git push
