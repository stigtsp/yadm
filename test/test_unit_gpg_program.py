import pytest


class Test_Unit_Gpg_Program(object):
    """Unit tests: yadm.gpg-program"""

    @ pytest.mark.parametrize(
        'program, code, value, match', [
            (None, 0, 'gpg', None),
            ('cat', 0, 'cat', None),
            ('badprogram', 1, None, 'badprogram'),
        ], ids=[
            'gpg missing',
            'valid alternative',
            'invalid alternative',
        ])
    def test_gpg_program(self, runner, paths, program, code, value, match):
        """Set yadm.gpg-program, and test result of require_gpg"""

        # set configuration
        if program:
            runner(command=[
                'git',
                'config',
                '--file=%s' % paths.config,
                'yadm.gpg-program',
                program,
            ]).report()

        # test require_gpg
        script = """
            YADM_TEST=1 source %s
            YADM_CONFIG="%s"
            require_gpg
            echo $GPG_PROGRAM
        """ % (paths.pgm, paths.config)
        run = runner(command=['bash'], inp=script)

        print script
        run.report()
        # correct exit code
        assert run.code == code

        # GPG_PROGRAM set correctly
        if value:
            assert run.out.rstrip() == value

        # error reported about bad config
        if match:
            assert match in run.out
