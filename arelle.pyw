'''
Created on Feb 19, 2011

Use this module to start Arelle in windowing interactive UI or command line modes

If no arguments, start in GUI mode

If any argument, start in command line mode

@author: Mark V Systems Limited
See COPYRIGHT.md for copyright info.
'''
import sys
from arelle import CntlrWinMain, CntlrCmdLine

if len(sys.argv) == 1:  # no command line arguments
    CntlrWinMain.main()
else:
    CntlrCmdLine.main()