#!/usr/bin/python
# 
# 
import sys
import gitconnector

# class Usage(Exception):
#     def __init__(self, msg):
#         self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        if len(argv) < 2:
            raise Exception("no subcommand given")
        subcmd = argv[1]
        args = argv[2:]

        if subcmd == "pre-commit":
            if len(args) != 0:
                raise Exception("pre-commit takes no argument")
            return gitconnector.pre_commit_hook()

        elif subcmd == "commit-msg":
            if len(args) != 1:
                raise Exception("pre-commit takes exactly one argument")
            return gitconnector.commit_msg_hook(args[0])

        elif subcmd == "prepare-commit-msg":
            if len(args)==0 or len(args)>3:
                raise Exception("prepare-commit-msg takes one to three arguments")
            return gitconnector.prepare_commit_msg_hook(args)

        elif subcmd == "update":
            if len(args) != 3:
                raise Exception("update takes exactly three arguments")
            return gitconnector.update_hook(args[0],args[1],args[2])
            
        else:
            raise Exception("Unknown subcommand: " + subcmd)

    # except Usage, err:
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())
