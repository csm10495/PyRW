'''
Brief:
    Quick script to install and then play with pyrw

Author(s):
    Charles Machalow
'''

import os
import sys

THIS_FILE = os.path.abspath(__file__)
THIS_FOLDER = os.path.abspath(os.path.dirname(THIS_FILE))

if __name__ == '__main__':
    if 'TEST_AND_GO' in os.environ:
        from pyrw.rwe import ReadWriteEverything
        rwe = ReadWriteEverything()
        print ('| --------------------------------------------- |')
        print ('| rwe object has been created for your usage... |')
        print ('| --------------------------------------------- |')
        # we should be interactive..
    else:
        os.chdir(THIS_FOLDER)
        os.system('%s -m pip install . --force-reinstall > nul 2>&1' % sys.executable)
        os.environ['TEST_AND_GO'] = '1'
        os.system('%s -i %s' % (sys.executable, THIS_FILE))
