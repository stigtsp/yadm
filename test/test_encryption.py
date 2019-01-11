"""Test encryption"""
import os
import pipes
import pytest

PASSPHRASE = 'ExamplePassword'

# Coverage:
# [ ] "Command 'encrypt' (missing YADM_ENCRYPT)"
# [ ] "Command 'encrypt' (mismatched password)"
# [X] "Command 'encrypt'"
# [X] "Command 'encrypt' (comments in YADM_ENCRYPT)"
# [X] "Command 'encrypt' (empty lines and space lines in YADM_ENCRYPT)"
# [X] "Command 'encrypt' (paths with spaces/globs in YADM_ENCRYPT)"
# [X] "Command 'encrypt' (exclusions in YADM_ENCRYPT)"
# [X] "Command 'encrypt' (directories in YADM_ENCRYPT)"
# [ ] "Command 'encrypt' (overwrite)"
#
# [ ] "Command 'decrypt' (missing YADM_ARCHIVE)"
# [ ] "Command 'decrypt' (wrong password)"
# [ ] "Command 'decrypt' -l (wrong password)"
# [ ] "Command 'decrypt'"
# [ ] "Command 'decrypt' (overwrite)"
# [ ] "Command 'decrypt' -l"
#
# [ ] "Command 'encrypt' (asymmetric, missing key)"
# [ ] "Command 'encrypt' (asymmetric)"
# [ ] "Command 'encrypt' (asymmetric, overwrite)"
# [ ] "Command 'encrypt' (asymmetric, ask)"
#
# [ ] "Command 'decrypt' (asymmetric, missing YADM_ARCHIVE)"
# [ ] "Command 'decrypt' (asymmetric, missing key)"
# [ ] "Command 'decrypt' -l (asymmetric, missing key)"
# [ ] "Command 'decrypt' (asymmetric)"
# [ ] "Command 'decrypt' (asymmetric, overwrite)"
# [ ] "Command 'decrypt' -l (asymmetric)"
#
# [ ] "Command 'encrypt' (offer to track YADM_ENCRYPT) NEW"


@pytest.fixture
def encrypt_targets(yadm_y, paths):
    """Fixture for setting up encryption

    This fixture:
      * inits an empty repo
      * creates test files in the work tree
      * creates a ".yadm/encrypt" file for testing:
        * standard files
        * standard globs
        * directories
        * comments
        * empty lines and lines with just space
        * exclusions
      * returns a list of expected encrypted files
    """

    # init empty yadm repo
    os.system(' '.join(yadm_y('init', '-w', str(paths.work), '-f')))

    expected = []

    # standard files w/ dirs & spaces
    paths.work.join('inc file1').write('inc file1')
    expected.append('inc file1')
    paths.encrypt.write('inc file1\n')
    paths.work.join('inc dir').mkdir()
    paths.work.join('inc dir/inc file2').write('inc file2')
    expected.append('inc dir/inc file2')
    paths.encrypt.write('inc dir/inc file2\n', mode='a')

    # standard globs w/ dirs & spaces
    paths.work.join('globs file1').write('globs file1')
    expected.append('globs file1')
    paths.work.join('globs dir').mkdir()
    paths.work.join('globs dir/globs file2').write('globs file2')
    expected.append('globs dir/globs file2')
    paths.encrypt.write('globs*\n', mode='a')

    # blank lines
    paths.encrypt.write('\n        \n\t\n', mode='a')

    # comments
    paths.work.join('commentfile1').write('commentfile1')
    paths.encrypt.write('#commentfile1\n', mode='a')
    paths.encrypt.write('        #commentfile1\n', mode='a')

    # exclusions
    paths.work.join('extest').mkdir()
    paths.encrypt.write('extest/*\n', mode='a')  # include within extest
    paths.work.join('extest/inglob1').write('inglob1')
    paths.work.join('extest/exglob1').write('exglob1')
    paths.work.join('extest/exglob2').write('exglob2')
    paths.encrypt.write('!extest/ex*\n', mode='a')  # exclude the ex*
    expected.append('extest/inglob1')  # should be left with only in*

    return expected


def test_enc(runner, yadm_y, paths, encrypt_targets):
    """WIP"""
    run = runner(yadm_y('encrypt'), expect=[
        ('passphrase:', PASSPHRASE),
        ('passphrase:', PASSPHRASE),
        ])
    print(run.out)
    assert run.code == 0
    assert encrypted_data_valid(runner, paths.archive, encrypt_targets)


def encrypted_data_valid(runner, encrypted, expected):
    """Verify encrypted data matches expectations"""
    run = runner([
        'gpg',
        '--passphrase', pipes.quote(PASSPHRASE),
        '-d', pipes.quote(str(encrypted)),
        '2>/dev/null',
        '|', 'tar', 't'], shell=True)
    file_count = 0
    for filename in run.out.splitlines():
        if filename.endswith('/'):
            continue
        file_count += 1
        assert filename in expected, (
            f'Unexpected file in archive: {filename}')
    assert file_count == len(expected), (
        'Number of files in archive does not match expected')
    return True
