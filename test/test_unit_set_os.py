"""Unit tests: set_operating_system"""
import pytest


@pytest.fixture(scope='module')
def uname(runner):
    """Value of `uname -s`"""
    run = runner(command=['uname', '-s'])
    return run.out.rstrip()


@pytest.mark.parametrize(
    'proc_value, expected_os', [
        ('missing', 'uname'),
        ('has Microsoft inside', 'WSL'),
        ('another value', 'uname'),
    ], ids=[
        '/proc/version missing',
        '/proc/version includes MS',
        '/proc/version excludes MS',
    ])
def test_set_operating_system(
        runner, paths, uname, proc_value, expected_os):
    """Run ,set_operating_system and test result"""
    proc_version = paths.root.join('proc_version')
    if proc_value != 'missing':
        proc_version.write(proc_value)
    script = """
        YADM_TEST=1 source %s
        PROC_VERSION=%s
        set_operating_system
        echo $OPERATING_SYSTEM
    """ % (paths.pgm, proc_version)
    run = runner(command=['bash'], inp=script)
    print(script)
    run.report()
    if expected_os == 'uname':
        expected_os = uname
    assert run.out.rstrip() == expected_os
