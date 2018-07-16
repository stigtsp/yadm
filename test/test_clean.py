class Test_Clean(object):
    """Clean"""

    def test_clean_command(self, runner, yadm_y):
        """Run with clean command"""
        run = runner(command=yadm_y('clean'))
        run.report()
        # do nothing, this is a dangerous Git command when managing dot files
        # report the command as disabled
        assert 'disabled' in run.out
        # and exit with 1
        assert run.code == 1
