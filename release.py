import re
import commands
import os
import sys
import readline
from optparse import OptionParser

WD = os.path.abspath(os.path.split(__file__)[0])
os.chdir(WD)

parser = OptionParser()
parser.add_option("--notest", dest="notest", action='store_true')
parser.add_option("--simulate", dest="simulate", action='store_true')
parser.add_option("--verbose", dest="verbose", action='store_true')
parser.add_option("--doconly", dest="doconly", action='store_true')

(options, args) = parser.parse_args()

def _ex(cmd, interrupt=True):
    if options.verbose or options.simulate:
        print "***", cmd
    if not options.simulate:
        s = os.system(cmd)
        if s != 0 and interrupt:
            sys.exit(s)
        else:
            return s
    else:
        return 0

def ask(string, valid_values, default=-1, case_sensitive=False):
    """ Asks for a keyborad answer """

    v = None
    if not case_sensitive:
        valid_values = [value.lower() for value in valid_values]
    while v not in valid_values:
        readline.set_startup_hook(lambda: readline.insert_text(default))
        try:
            v = raw_input("%s [%s] " % (string, ', '.join(valid_values))).strip()
            if v == '' and default>=0:
                v = valid_values[default]
            if not case_sensitive:
                v = v.lower()
        finally:
            readline.set_startup_hook()
    return v

def ask_path(string, default_path):
    v = None
    while v is None:
        v = raw_input("%s [%s] " % (string, default_path)).strip()
        if v == '':
            v = default_path
        if not os.path.exists(v):
            print >>sys.stderr, v, "does not exist."
            v = None
    return v

TEMP_PATH = "/tmp"
CURRENT_VERSION = open('VERSION').readline().strip()
a, b, c, tag, ncom, hcom  = re.search("(\d+)\.(\d+)\.(\d+)(-?\w+\d+)?-?(\d+)?-?(\w+)?", CURRENT_VERSION).groups()
a, b, c = map(int, (a, b, c))
SERIES_VERSION = "%s.%s" %(a, b)
print '===================================================='
print 'CURRENT VERSION:', a, b, c, tag, ncom, hcom
print '===================================================='
# test examples
raw_input('continue?')

if not options.doconly:
    # commit changes in VERSION
    if tag:
        tag1, tag2 = re.search('(.+?)(\d+)', tag).groups()
        tag2 = int(tag2)
        NEW_VERSION = "%s.%s.%s%s%s" %(a, b, c, tag1, tag2+1)
    else:
        NEW_VERSION = "%s.%s.%s" %(a, b, c+1)

    if ask('Increase version to "%s" ?' %NEW_VERSION, ['y', 'n']) == 'n':
        NEW_VERSION = raw_input('new version string:').strip()

    if ask('Write "%s" and commit changes?' %NEW_VERSION, ['y', 'n']) == 'y':
        open('VERSION', 'w').write(NEW_VERSION)
        open("eggnogmapper/version.py", 'w').write("#autogenerated during release process. Do not modify\n__VERSION__='%s'\n" %(NEW_VERSION))
        _ex('git commit -a -m "release %s " && git tag -f %s' %(NEW_VERSION, NEW_VERSION))

sys.exit(0)

