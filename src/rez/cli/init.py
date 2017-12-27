"""
Initialize the rez configuration file for current package.
"""

import uuid
import os
import shutil
import getpass
import sys
from rez import module_root_path

TEMPLATE_DIR = os.path.join(os.path.dirname(module_root_path),
                            'templates')
PACKAGE_PY_FILE = 'package.py'
TEMPLATE_PACAKGE_PY_FILE = os.path.join(TEMPLATE_DIR, PACKAGE_PY_FILE)

OTHER_FILES = ['rezbuild.py']

PACKAGE_NAME_STR = 'PACKAGE_NAME'
AUTHORS_STR = 'AUTHORS'
DESCRIPTION_STR = 'DESCRIPTION'
UUID_STR = 'UUID'
VERSION_STR = 'VERSION'
COMMANDS_STR = 'COMMANDS'


def copyPackagePy(dstDir='', srcFile=TEMPLATE_PACAKGE_PY_FILE, **kwargs):
    dstFile = os.path.join(dstDir, PACKAGE_PY_FILE)
    if os.path.isfile(dstFile):
        return

    with open(dstFile, 'w') as w:
        with open(srcFile, 'r') as f:
            for line in f.xreadlines():
                """
                @Fixme, have to add root='{root}' 
                 to handle command replacement problem.
                """
                newLine = line.format(root='{root}', **kwargs)
                w.write(newLine)

    print "{0} -> {1}".format(srcFile, dstFile)


def copyOtherFiles(currentDir):
    for fileName in OTHER_FILES:
        src = os.path.join(TEMPLATE_DIR, fileName)
        dst = os.path.join(currentDir, fileName)
        if os.path.isfile(dst):
            os.remove(dst)
        shutil.copy2(src, dst)


def setupGitignore(currentDir):
    """
    Added gitignore list into .gitignore file.
    """
    GITIGNORE_LIST = ['.build', '*.pyc']
    GITIGNORE_FILE_NAME = '.gitignore'
    
    gitignorePath = os.path.join(currentDir, GITIGNORE_FILE_NAME)

    checkMap = {item: False for item in GITIGNORE_LIST}

    with open(gitignorePath, 'a+r') as f:
        for line in f:
            for item in checkMap.keys():
                if item in line:
                    checkMap[item] = True
        else:
            for item, isExisted in checkMap.iteritems():
                if not isExisted:
                    f.write(str(item))
                    f.write('\n')


def createBaseFolder(currentDir):
    """
    create some basic folders
    """
    basicFolders = ['src', 'bin']
    for basicFolder in basicFolders:
        folderPath = os.path.join(currentDir, basicFolder)
        if not os.path.isdir(folderPath):
            os.makedirs(folderPath)


def setup_parser(parser, completions=False):
    parser.add_argument(
        "-d", "--description", dest="description",
        help="Add some description to package.py",
        type=str, default='No Description')
    parser.add_argument(
        "-t", "--type", dest="type",
        help="Give a package type of your package, [python|runtime|dcc]",
        type=str, default='python')
    parser.add_argument(
        "-pv", "--packageversion", dest="packageVersion",
        help="Add the version to package.py",
        type=str, default='0.0.0')
    parser.add_argument(
        "-vc", "--versioncopy", action="store_true",
        help="Copy package.py to each verison folder, just for dcc and runtime.")
    parser.add_argument(
        "-ac", "--addcommand", action="store_true",
        help="Please don't use this.")
    parser.add_argument(
        "-abc", "--addbincommand", action="store_true",
        help="Please don't use this.")
    parser.add_argument(
        "-asc", "--addsrccommand", action="store_true",
        help="Please don't use this.")
    parser.add_argument(
        "-alc", "--addlibcommand", action="store_true",
        help="Please don't use this.")


def initPythonPackage(currentDir, opts, **kwargs):
    print 'Initializing Python Package...\n'

    kwargs.update({PACKAGE_NAME_STR: os.path.basename(currentDir),
                   AUTHORS_STR: getpass.getuser(),
                   VERSION_STR: opts.packageVersion})

    copyPackagePy(currentDir, **kwargs)
    copyOtherFiles(currentDir)
    setupGitignore(currentDir)
    createBaseFolder(currentDir)


def initDccPackage(currentDir, opts, **kwargs):
    print 'Initializing DCC Package...\n'

    kwargs.update({PACKAGE_NAME_STR: os.path.basename(currentDir),
                   AUTHORS_STR: os.path.basename(currentDir),
                   VERSION_STR: r'{VERSION}'})

    copyPackagePy(currentDir, **kwargs)


def initRuntimePackage(currentDir, opts, **kwargs):
    print 'Initializing Runtime Package...\n'

    kwargs.update({PACKAGE_NAME_STR: os.path.basename(currentDir),
                   AUTHORS_STR: os.path.basename(currentDir),
                   VERSION_STR: r'{VERSION}'})

    copyPackagePy(currentDir, **kwargs)


def versionCopy(currentDir, opts):
    packagePyFile = os.path.join(currentDir, PACKAGE_PY_FILE)
    if not os.path.isfile(packagePyFile):
        print >> sys.stderr, '[ERROR] No Package.py here, please run "rez-init" first"!'

    if opts.packageVersion == '0.0.0':
        for version in os.listdir(currentDir):
            if os.path.isdir(version):
                disDir = os.path.join(currentDir, version)
                kwargs = {VERSION_STR: version}
                copyPackagePy(dstDir=disDir, srcFile=packagePyFile, **kwargs)
    else:
        disDir = os.path.join(currentDir, version)
        kwargs = {VERSION_STR: version}
        copyPackagePy(dstDir=disDir, srcFile=packagePyFile, **kwargs)

    os.remove(packagePyFile)


def getCommand(opts):
    cmds = []

    if opts.type in ('python'):
        cmds.append('env.PYTHONPATH.append("{root}")')
        cmds.append('env.PATH.append("{root}/bin")')

    elif opts.type in ('runtime'):
        cmds.append('env.LD_LIBRARY_PATH.append("{root}/lib")')
    elif opts.type in ('dcc'):
        cmds.append('env.PATH.append("{root}/bin")')

    return '\n    '.join(cmds)


def addCommand(currentDir, opts):
    print 'Adding NEW commands...\n'
    packagePyFile = os.path.join(currentDir, PACKAGE_PY_FILE)
    cmds = []

    if opts.addbincommand:
        cmds.append('env.PATH.append("{root}/bin")')

    if opts.addsrccommand:
        cmds.append('env.PYTHONPATH.append("{root}/src")')

    if opts.addlibcommand:
        cmds.append('env.LD_LIBRARY_PATH.append("{root}/lib")')

    cmd = '\n    '.join(cmds)

    if not os.path.isfile(packagePyFile):
        print >> sys.stderr, '[ERROR] No package.py file, please run "rez-ini"!'
        return

    with open(packagePyFile, 'a') as f:
        f.write('\n    ')
        f.write(cmd)

    print 'Add new commands:'
    print '    ' + cmd


def command(opts, parser, extra_arg_groups=None):
    currentDir = os.getcwd()

    if opts.addcommand:
        """
        AddCommand mode means, open package file append some specified comamnds.
        """
        addCommand(currentDir, opts)
        return

    kwargs = {UUID_STR: str(uuid.uuid4()), 
              DESCRIPTION_STR: opts.description,
              COMMANDS_STR: getCommand(opts)}

    if opts.type == 'python':
        if opts.versioncopy:
            print >> sys.stderr, '[ERROR] Only dcc/runtime package has "-vc" mode.'
        else:
            initPythonPackage(currentDir, opts, **kwargs)

    elif opts.type == 'dcc':
        if opts.versioncopy:
            versionCopy(currentDir, opts)
        else:
            initDccPackage(currentDir, opts, **kwargs)

    elif opts.type == 'runtime':
        if opts.versioncopy:
            versionCopy(currentDir, opts)
        else:
            initRuntimePackage(currentDir, opts, **kwargs)

    else:
        print >> sys.stderr, '[ERROR] Package Type Error, please see the help(rez-init -h)!'
