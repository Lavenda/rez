import os
import os.path
import shutil
import stat


def build(source_path, build_path, install_path, targets):

    src_dirs = ['src']
    bin_dirs = ['bin']

    def _build():

        # source file
        for src_dir in src_dirs:

            src = os.path.join(source_path, src_dir)
            dest = os.path.join(build_path, src_dir)

            if not os.path.exists(dest):
                shutil.copytree(src, dest, 
                                ignore=shutil.ignore_patterns('*.pyc'))

        # binaries
        mode = (stat.S_IRUSR | stat.S_IRGRP |
                stat.S_IXUSR | stat.S_IXGRP)

        for bin_dir in bin_dirs:
            src_bin = os.path.join(source_path, bin_dir)
            dest_bin = os.path.join(build_path, bin_dir)

            if not os.path.exists(dest_bin):
                shutil.copytree(src_bin, dest_bin)

                for name in os.listdir(dest_bin):
                    filepath = os.path.join(dest_bin, name)
                    os.chmod(filepath, mode)


    def _install():
        for name in (src_dirs + bin_dirs):
            src = os.path.join(build_path, name)
            dest = os.path.join(install_path, name)

            if os.path.exists(dest):
                shutil.rmtree(dest)

            print "{0} -> {1}".format(src, dest)
            shutil.copytree(src, dest)

    _build()

    if "install" in (targets or []):
        _install()
