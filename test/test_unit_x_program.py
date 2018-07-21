"""Unit tests: yadm.[git,gpg]-program"""
import pytest


@pytest.mark.parametrize(
    'executable, code, value, match', [
        (None, 0, 'program', None),
        ('cat', 0, 'cat', None),
        ('badprogram', 1, None, 'badprogram'),
    ], ids=[
        'executable missing',
        'valid alternative',
        'invalid alternative',
    ])
@pytest.mark.parametrize('program', ['git', 'gpg'])
def test_x_program(runner, paths, program, executable, code, value, match):
    """Set yadm.X-program, and test result of require_X"""

    # set configuration
    if executable:
        runner(command=[
            'git',
            'config',
            '--file=%s' % paths.config,
            'yadm.%s-program' % program,
            executable,
        ]).report()

    # test require_[git,gpg]
    script = """
        YADM_TEST=1 source %s
        YADM_CONFIG="%s"
        require_%s
        echo $%s_PROGRAM
    """ % (paths.pgm, paths.config, program, program.upper())
    run = runner(command=['bash'], inp=script)

    print script
    run.report()
    # correct exit code
    assert run.code == code

    # [GIT,GPG]_PROGRAM set correctly
    if value == 'program':
        assert run.out.rstrip() == program
    elif value:
        assert run.out.rstrip() == value

    # error reported about bad config
    if match:
        assert match in run.out
