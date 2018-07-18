import collections
import pytest


class Test_Unit_Git_Program(object):
    """Unit tests: yadm.git-program"""

    Option = collections.namedtuple(
        'Option', ['program', 'code', 'value', 'match'])

    @pytest.fixture(params=[
        Option(None, 0, 'git', None),
        Option('cat', 0, 'cat', None),
        Option('badprogram', 1, None, 'badprogram'),
        ])
    def option(self, request):
        """Test options; program, expected code"""
        return request.param

    def test_git_program(self, runner, paths, option):
        """Set yadm.git-program, and test result of require_git"""

        # set configuration
        if option.program:
            runner(command=[
                'git',
                'config',
                '--file=%s' % paths.config,
                'yadm.git-program',
                option.program,
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
        assert run.code == option.code

        # GIT_PROGRAM set correctly
        if option.value:
            assert run.out.rstrip() == option.value

        # error reported about bad config
        if option.match:
            assert option.match in run.out
