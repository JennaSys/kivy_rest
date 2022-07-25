import subprocess
import sys

from src.version import __version__


VERSION_FILE = 'src/version.py'

levels = dict(major=0, minor=1, patch=2)


def get_new_version(level=None) -> str:
    version_nums = [int(ver) for ver in __version__.split('.')]

    if level is not None:
        for lev_num in range(level, 3):
            if lev_num == level:
                version_nums[lev_num] += 1
            else:
                version_nums[lev_num] = 0

    return '.'.join([str(ver_num) for ver_num in version_nums])


def tag_git(semver) -> bool:
    clean = subprocess.check_output(['git', 'status', '--porcelain']) == b''

    if clean:
        try:
            update_local(semver)
            subprocess.check_output(['git', 'add', VERSION_FILE])
            subprocess.check_output(['git', 'commit', '-m', f'Version {semver}'])
            subprocess.check_output(['git', 'tag', f'v{semver}'])
            return True
        except Exception as e:
            print(e)
    else:
        print(f"ERROR: Git repository is not clean!  Commit changes and try again")
        return False


def update_local(semver):
    with open(VERSION_FILE, 'w') as version_file:
        version_file.write(f'__version__ = "{semver}"\n')


def main():
    if len(sys.argv) > 1:
        level_name = sys.argv[1]
        if level_name in levels:
            new_semver = get_new_version(levels[level_name])

            if tag_git(new_semver):
                print(f'Version updated to {new_semver}')

        else:
            print(f"ERROR: '{level_name}' is not a valid semver level!")
    else:
        current_ver = get_new_version()
        print(f'Version is currently at {current_ver}')


if __name__ == '__main__':
    main()
