import pytest


class Test_Unit_Git_Program(object):
    """Unit tests: yadm.git-program"""

    @ pytest.mark.parametrize(
        'program, code, value, match', [
            (None, 0, 'git', None),
            ('cat', 0, 'cat', None),
            ('badprogram', 1, None, 'badprogram'),
        ], ids=[
            'git missing',
            'valid alternative',
            'invalid alternative',
        ])
    def test_git_program(self, runner, paths, program, code, value, match):
        """Set yadm.git-program, and test result of require_git"""

        # set configuration
        if program:
            runner(command=[
                'git',
                'config',
                '--file=%s' % paths.config,
                'yadm.git-program',
                program,
            ]).report()

        # test require_git
        script = """
            YADM_TEST=1 source %s
            YADM_CONFIG="%s"
            require_git
            echo $GIT_PROGRAM
        """ % (paths.pgm, paths.config)
        run = runner(command=['bash'], inp=script)

        print script
        run.report()
        # correct exit code
        assert run.code == code

        # GIT_PROGRAM set correctly
        if value:
            assert run.out.rstrip() == value

        # error reported about bad config
        if match:
            assert match in run.out
