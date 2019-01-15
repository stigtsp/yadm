"""Test encryption"""
import os
import pipes
import pytest

PASSPHRASE = 'ExamplePassword'

# Coverage:
# [X] "Command 'encrypt' (missing YADM_ENCRYPT)"
# [X] "Command 'encrypt' (mismatched password)"
# [X] "Command 'encrypt'"
# [X] "Command 'encrypt' (comments in YADM_ENCRYPT)"
# [X] "Command 'encrypt' (empty lines and space lines in YADM_ENCRYPT)"
# [X] "Command 'encrypt' (paths with spaces/globs in YADM_ENCRYPT)"
# [X] "Command 'encrypt' (exclusions in YADM_ENCRYPT)"
# [X] "Command 'encrypt' (directories in YADM_ENCRYPT)"
# [X] "Command 'encrypt' (overwrite)"
#
# [X] "Command 'decrypt' (missing YADM_ARCHIVE)"
# [X] "Command 'decrypt' (wrong password)"
# [X] "Command 'decrypt' -l (wrong password)"
# [X] "Command 'decrypt'"
# [X] "Command 'decrypt' (overwrite)"
# [X] "Command 'decrypt' -l"
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
    """Fixture for setting up data to encrypt

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


@pytest.fixture(scope='session')
def decrypt_targets(tmpdir_factory, runner):
    """Fixture for setting data to decrypt

    This fixture:
      * creates an encrypted archive
      * creates a list of expected decrypted files
    """

    tmpdir = tmpdir_factory.mktemp('decrypt_targets')
    archive = tmpdir.join('archive.tar.gz.gpg')

    expected = []

    tmpdir.join('decrypt1').write('decrypt1')
    expected.append('decrypt1')
    tmpdir.join('decrypt2').write('decrypt2')
    expected.append('decrypt2')
    tmpdir.join('subdir').mkdir()
    tmpdir.join('subdir/decrypt3').write('subdir/decrypt3')
    expected.append('subdir/decrypt3')

    run = runner(
        ['tar', 'cvf', '-'] +
        expected +
        ['|', 'gpg', '--yes', '-c'] +
        ['--passphrase', pipes.quote(PASSPHRASE)] +
        ['--output', pipes.quote(str(archive))],
        cwd=tmpdir,
        shell=True)
    run.report()
    assert run.code == 0

    return {'archive': archive, 'expected': expected}


@pytest.mark.parametrize(
    'mismatched_phrase', [False, True],
    ids=['matching_phrase', 'mismatched_phrase'])
@pytest.mark.parametrize(
    'missing_encrypt', [False, True],
    ids=['encrypt_exists', 'encrypt_missing'])
@pytest.mark.parametrize(
    'overwrite', [False, True],
    ids=['clean', 'overwrite'])
def test_symmetric_encrypt(
        runner, yadm_y, paths, encrypt_targets,
        overwrite, missing_encrypt, mismatched_phrase):
    """Test symmetric encryption"""

    if missing_encrypt:
        paths.encrypt.remove()

    matched_phrase = PASSPHRASE
    if mismatched_phrase:
        matched_phrase = 'mismatched'

    if overwrite:
        paths.archive.write('existing archive')

    run = runner(yadm_y('encrypt'), expect=[
        ('passphrase:', PASSPHRASE),
        ('passphrase:', matched_phrase),
        ])
    run.report()

    if missing_encrypt or mismatched_phrase:
        assert run.code == 1
    else:
        assert run.code == 0

    if missing_encrypt:
        assert 'does not exist' in run.out
    elif mismatched_phrase:
        assert 'invalid passphrase' in run.out
    else:
        assert encrypted_data_valid(runner, paths.archive, encrypt_targets)


@pytest.mark.parametrize(
    'wrong_phrase', [False, True],
    ids=['correct_phrase', 'wrong_phrase'])
@pytest.mark.parametrize(
    'archive_exists', [True, False],
    ids=['archive_exists', 'archive_missing'])
@pytest.mark.parametrize(
    'overwrite', [False, True],
    ids=['clean', 'overwrite'])
@pytest.mark.parametrize(
    'dolist', [False, True],
    ids=['decrypt', 'list'])
def test_symmetric_decrypt(
        runner, yadm_y, paths, decrypt_targets,
        dolist, overwrite, archive_exists, wrong_phrase):
    """Test symmetric decryption"""

    # init empty yadm repo
    os.system(' '.join(yadm_y('init', '-w', str(paths.work), '-f')))

    phrase = PASSPHRASE
    if wrong_phrase:
        phrase = 'wrong-phrase'

    if archive_exists:
        decrypt_targets['archive'].copy(paths.archive)

    if overwrite:
        paths.work.join('decrypt1').write('pre-existing file')

    args = []
    if dolist:
        args.append('-l')
    run = runner(yadm_y('decrypt') + args, expect=[
        ('passphrase:', phrase)
        ])
    run.report()

    if archive_exists and not wrong_phrase:
        assert run.code == 0
        if dolist:
            for filename in decrypt_targets['expected']:
                if not overwrite or filename != 'decrypt1':
                    assert not paths.work.join(filename).exists()
                assert filename in run.out
        else:
            for filename in decrypt_targets['expected']:
                assert paths.work.join(filename).read() == filename
    else:
        assert run.code == 1


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
