#!/usr/bin/python
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
