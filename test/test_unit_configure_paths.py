"""Unit tests: configure_paths"""
import pytest

HOME = '/testhome'
YDIR = '.yadm'
REPO = 'repo.git'
CONFIG = 'config'
ENCRYPT = 'encrypt'
ARCHIVE = 'files.gpg'
BOOTSTRAP = 'bootstrap'


@pytest.mark.parametrize(
    'override, expect', [
        (None, {}),
        ('-Y', {}),
        ('--yadm-repo', {'repo': 'YADM_REPO', 'git': 'GIT_DIR'}),
        ('--yadm-config', {'config': 'YADM_CONFIG'}),
        ('--yadm-encrypt', {'encrypt': 'YADM_ENCRYPT'}),
        ('--yadm-archive', {'archive': 'YADM_ARCHIVE'}),
        ('--yadm-bootstrap', {'bootstrap': 'YADM_BOOTSTRAP'}),
    ], ids=[
        'default',
        'override yadm dir',
        'override repo',
        'override config',
        'override encrypt',
        'override archive',
        'override bootstrap',
    ])
def test_config(runner, paths, override, expect):
    """Test configure_paths"""
    opath = 'override'
    matches = match_map()
    args = []
    if override == '-Y':
        matches = match_map('/' + opath)

    if override:
        args = [override, '/' + opath]
        for ekey in expect.keys():
            matches[ekey] = '%s="/%s"' % (expect[ekey], opath)
        run_test(
            runner, paths,
            [override, opath],
            ['must specify a fully qualified'], 1)

    run_test(runner, paths, args, matches.values(), 0)


def match_map(yadm_dir=None):
    """Create a dictionary of matches, relative to yadm_dir"""
    if not yadm_dir:
        yadm_dir = '/'.join([HOME, YDIR])
    return {
        'yadm': 'YADM_DIR="%s"' % yadm_dir,
        'repo': 'YADM_REPO="%s"' % '/'.join([yadm_dir, REPO]),
        'config': 'YADM_CONFIG="%s"' % '/'.join([yadm_dir, CONFIG]),
        'encrypt': 'YADM_ENCRYPT="%s"' % '/'.join([yadm_dir, ENCRYPT]),
        'archive': 'YADM_ARCHIVE="%s"' % '/'.join([yadm_dir, ARCHIVE]),
        'bootstrap': 'YADM_BOOTSTRAP="%s"' % '/'.join([yadm_dir, BOOTSTRAP]),
        'git': 'GIT_DIR="%s"' % '/'.join([yadm_dir, REPO]),
        }


def run_test(runner, paths, args, expected_matches, expected_code=0):
    """Run proces global args, and run configure_paths"""
    argstring = ' '.join(['"'+a+'"' for a in args])
    script = """
        YADM_TEST=1 HOME="%s" source %s
        process_global_args %s
        configure_paths
        declare -p | grep -E '(YADM|GIT)_'
    """ % (HOME, paths.pgm, argstring)
    run = runner(command=['bash'], inp=script)
    print script
    run.report()
    assert run.code == expected_code
    for match in expected_matches:
        assert match in run.out
