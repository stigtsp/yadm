"""Unit tests: configure_paths"""

HOME = '/testhome'
YDIR = '.yadm'
REPO = 'repo.git'
CONFIG = 'config'
ENCRYPT = 'encrypt'
ARCHIVE = 'files.gpg'
BOOTSTRAP = 'bootstrap'


def test_paths_default(runner, paths):
    """Default paths"""
    matches = match_map()
    run_test(runner, paths, [], matches.values(), 0)


def test_paths_override_yadm(runner, paths):
    """Override yadm_dir"""
    # not fully qualified
    run_test(
        runner, paths,
        ['-Y', 'override'],
        ['must specify a fully qualified'], 1)

    # fully qualified
    matches = match_map('/override')
    run_test(
        runner, paths,
        ['-Y', '/override'],
        matches.values(), 0)


def test_paths_override_repo(runner, paths):
    """Override yadm_repo"""
    # not fully qualified
    run_test(
        runner, paths,
        ['--yadm-repo', 'override'],
        ['must specify a fully qualified'], 1)

    # fully qualified
    matches = match_map()
    matches['repo'] = 'YADM_REPO="%s"' % '/override'
    matches['git'] = 'GIT_DIR="%s"' % '/override'
    run_test(
        runner, paths,
        ['--yadm-repo', '/override'],
        matches.values(), 0)


def test_paths_override_config(runner, paths):
    """Override yadm_config"""
    # not fully qualified
    run_test(
        runner, paths,
        ['--yadm-config', 'override'],
        ['must specify a fully qualified'], 1)

    # fully qualified
    matches = match_map()
    matches['config'] = 'YADM_CONFIG="%s"' % '/override'
    run_test(
        runner, paths,
        ['--yadm-config', '/override'],
        matches.values(), 0)


def test_paths_override_encrypt(runner, paths):
    """Override yadm_encrypt"""
    # not fully qualified
    run_test(
        runner, paths,
        ['--yadm-encrypt', 'override'],
        ['must specify a fully qualified'], 1)

    # fully qualified
    matches = match_map()
    matches['encrypt'] = 'YADM_ENCRYPT="%s"' % '/override'
    run_test(
        runner, paths,
        ['--yadm-encrypt', '/override'],
        matches.values(), 0)


def test_paths_override_archive(runner, paths):
    """Override yadm_archive"""
    # not fully qualified
    run_test(
        runner, paths,
        ['--yadm-archive', 'override'],
        ['must specify a fully qualified'], 1)

    # fully qualified
    matches = match_map()
    matches['archive'] = 'YADM_ARCHIVE="%s"' % '/override'
    run_test(
        runner, paths,
        ['--yadm-archive', '/override'],
        matches.values(), 0)


def test_paths_override_bootstrap(runner, paths):
    """Override yadm_bootstrap"""
    # not fully qualified
    run_test(
        runner, paths,
        ['--yadm-bootstrap', 'override'],
        ['must specify a fully qualified'], 1)

    # fully qualified
    matches = match_map()
    matches['bootstrap'] = 'YADM_BOOTSTRAP="%s"' % '/override'
    run_test(
        runner, paths,
        ['--yadm-bootstrap', '/override'],
        matches.values(), 0)


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
