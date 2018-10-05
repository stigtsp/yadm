"""Test alt"""
import os
import pytest

# coverage:
# [X] test untracked/unencrypted file linking
# [X] test tracked file linking
# [X] test encrypt entry linking
# [X] test overrides with local.os, local.hostname, local.user
# [X] test range of classes (upper/lower case)
# [X] test auto-alt settings (using the yadm status command)
# [X] test precedence (parametrize over an index, creating valid matching
#     suffixes, ensuring the highest precedence is linked

# [ ] test delimiter "_" does not work
# [ ] test recursion
# [X] test spaces in file names
# [X] test spaces in directory names

# precedence for matching:
#   ##
#   ##OS
#   ##OS.HOSTNAME
#   ##OS.HOSTNAME.USER
#   ##CLASS
#   ##CLASS.OS
#   ##CLASS.OS.HOSTNAME
#   ##CLASS.OS.HOSTNAME.USER

# PROBABLY: staticly define bogus files in data set, and then add positive
# test case during each test

FILE1 = 'test_alt'
FILE2 = 'test alt/test alt'


@pytest.mark.parametrize('precedence_index', range(8))
@pytest.mark.parametrize(
    'tracked, encrypt', [
        (False, False),
        (True, False),
        (False, True),
    ], ids=[
        'untracked',
        'tracked',
        'encrypted',
    ])
@pytest.mark.usefixtures('ds1_copy')
def test_alt(runner, yadm_y, paths,
             tst_sys, tst_host, tst_user,
             tracked, encrypt,
             precedence_index):
    """Test alternate linking"""

    # set the class
    tst_class = 'testclass'
    set_local(paths, 'class', tst_class)

    # define the expected precedence of suffix
    precedence = [
        f'##',
        f'##{tst_sys}',
        f'##{tst_sys}.{tst_host}',
        f'##{tst_sys}.{tst_host}.{tst_user}',
        f'##{tst_class}',
        f'##{tst_class}.{tst_sys}',
        f'##{tst_class}.{tst_sys}.{tst_host}',
        f'##{tst_class}.{tst_sys}.{tst_host}.{tst_user}',
    ]

    # create files using a subset of files
    for suffix in precedence[0:precedence_index+1]:
        create_files(paths, suffix, tracked=tracked, encrypt=encrypt)

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    run.report()
    assert run.code == 0

    # assert the proper linking has occurred
    for file_path in (FILE1, FILE2):
        if tracked or encrypt:
            assert paths.work.join(file_path).islink()
            assert paths.work.join(file_path).read() == (
                file_path + precedence[precedence_index])
        else:
            assert not paths.work.join(file_path).exists()


@pytest.mark.usefixtures('ds1_copy')
def test_local_override(runner, yadm_y, paths,
                        tst_sys, tst_host, tst_user):
    """Test local overrides"""

    # define local overrides
    set_local(paths, 'class', 'or-class')
    set_local(paths, 'hostname', 'or-hostname')
    set_local(paths, 'os', 'or-os')
    set_local(paths, 'user', 'or-user')

    # create files, the first would normally be the most specific version
    # however, the second is the overridden version which should be preferred.
    create_files(paths, f'##or-class.{tst_sys}.{tst_host}.{tst_user}')
    create_files(paths, '##or-class.or-os.or-hostname.or-user')

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    run.report()
    assert run.code == 0

    # assert the proper linking has occurred
    for file_path in (FILE1, FILE2):
        assert paths.work.join(file_path).islink()
        assert paths.work.join(file_path).read() == (
            file_path + '##or-class.or-os.or-hostname.or-user')


@pytest.mark.parametrize('suffix', ['AAA', 'ZZZ', 'aaa', 'zzz'])
@pytest.mark.usefixtures('ds1_copy')
def test_class_case(runner, yadm_y, paths, tst_sys, suffix):
    """Test range of class cases"""

    # set the class
    set_local(paths, 'class', suffix)

    # create files
    endings = [suffix]
    if tst_sys == 'Linux':
        # Only create all of these side-by-side on Linux, which is
        # unquestionably case-sensitive. This would break tests on
        # case-insensitive systems.
        endings = ['AAA', 'ZZZ', 'aaa', 'zzz']
    for ending in endings:
        create_files(paths, f'##{ending}')

    # run alt to trigger linking
    run = runner(yadm_y('alt'))
    run.report()
    assert run.code == 0

    # assert the proper linking has occurred
    for file_path in (FILE1, FILE2):
        assert paths.work.join(file_path).islink()
        assert paths.work.join(file_path).read() == (
            file_path + f'##{suffix}')


@pytest.mark.parametrize('autoalt', [None, 'true', 'false'])
@pytest.mark.usefixtures('ds1_copy')
def test_auto_alt(runner, yadm_y, paths, autoalt):
    """Test setting auto-alt"""

    # set the value of auto-alt
    if autoalt:
        os.system(' '.join(yadm_y('config', 'yadm.auto-alt', autoalt)))

    # create file
    create_files(paths, f'##')

    # run status to possibly trigger linking
    run = runner(yadm_y('status'))
    run.report()
    assert run.code == 0

    # assert the proper linking has occurred
    for file_path in (FILE1, FILE2):
        if autoalt == 'false':
            assert not paths.work.join(file_path).exists()
        else:
            assert paths.work.join(file_path).islink()
            assert paths.work.join(file_path).read() == (
                file_path + '##')


def set_local(paths, variable, value):
    """Set local override"""
    os.system(
        f'GIT_DIR={str(paths.repo)} '
        f'git config --local "local.{variable}" "{value}"'
    )


def create_files(paths, suffix, preserve=False, tracked=True, encrypt=False):
    """Create new file, and add to the repo"""

    if not preserve:
        if paths.work.join(FILE1).exists():
            paths.work.join(FILE1).remove(rec=1, ignore_errors=True)
            assert not paths.work.join(FILE1).exists()
        if paths.work.join(FILE2).exists():
            paths.work.join(FILE2).remove(rec=1, ignore_errors=True)
            assert not paths.work.join(FILE2).exists()

    new_file1 = paths.work.join(FILE1 + suffix)
    new_file1.write(FILE1 + suffix, ensure=True)
    new_file2 = paths.work.join(FILE2 + suffix)
    new_file2.write(FILE2 + suffix, ensure=True)
    assert new_file1.exists()
    assert new_file2.exists()

    if tracked:
        for path in (new_file1, new_file2):
            os.system(f'GIT_DIR={str(paths.repo)} git add "{path}"')
        os.system(f'GIT_DIR={str(paths.repo)} git commit -m "Add test files"')

    if encrypt:
        paths.encrypt.write(f'{FILE1 + suffix}\n', mode='a')
        paths.encrypt.write(f'{FILE2 + suffix}\n', mode='a')
