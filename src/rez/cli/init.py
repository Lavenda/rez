"""
Initialize the rez configuration file for current package.
"""

import uuid
import os
import shutil
import getpass
from rez import module_root_path

TEMPLATE_DIR = os.path.join(os.path.dirname(module_root_path),
                            'templates')
PACKAGE_PY_FILE = 'package.py'
OTHER_FILES = ['rezbuild.py']

PACKAGE_NAME_STR = '@PACKAGE_NAME@'
USR_NAME_STR = '@USER_NAME@'
DESCRIPTION_STR = '@DESCRIPTION@'
UUID_STR = '@UUID@'


def copyPackagePy(packageName, userName, description, currentDir, uuid):
    curPackageFile = os.path.join(currentDir, PACKAGE_PY_FILE)
    if os.path.isfile(curPackageFile):
        return

    packageFile = os.path.join(TEMPLATE_DIR, PACKAGE_PY_FILE)

    with open(curPackageFile, 'w') as w:
        with open(packageFile, 'r') as f:
            for line in f.xreadlines():
                if PACKAGE_NAME_STR in line:
                    newLine = line.replace(PACKAGE_NAME_STR, packageName)
                elif USR_NAME_STR in line:
                    newLine = line.replace(USR_NAME_STR, userName)
                elif DESCRIPTION_STR in line:
                    newLine = line.replace(DESCRIPTION_STR, description)
                elif UUID_STR in line:
                    newLine = line.replace(UUID_STR, uuid)
                else:
                    newLine = line

                w.write(newLine)


def copyOtherFiles(currentDir):
    for fileName in OTHER_FILES:
        src = os.path.join(TEMPLATE_DIR, fileName)
        dst = os.path.join(currentDir, fileName)
        if os.path.isfile(dst):
            os.remove(dst)
        shutil.copy2(src, dst)


def setupGitignore(currentDir):
    """
    Added [.build] folder into .gitignore file.
    """
    BUILD_FOLDER_NAME = '.build'
    GITIGNORE_FILE_NAME = '.gitignore'
    
    gitignorePath = os.path.join(currentDir, GITIGNORE_FILE_NAME)

    with open(gitignorePath, 'a+r') as f:
        for line in f:
            if BUILD_FOLDER_NAME in line:
                break
        else:
            f.write(BUILD_FOLDER_NAME)


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
        type=str)


def command(opts, parser, extra_arg_groups=None):
    currentDir = os.getcwd()
    userName = getpass.getuser()
    packageName = os.path.basename(currentDir)
    description = opts.description if opts.description else 'No Description'
    uuidStr = '"{0}"'.format(str(uuid.uuid4()))

    copyPackagePy(packageName, userName, description, currentDir, uuidStr)
    copyOtherFiles(currentDir)
    setupGitignore(currentDir)
    createBaseFolder(currentDir)
