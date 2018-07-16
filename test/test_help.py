class Test_Help(object):
    """Help"""

    def test_missing_command(self, runner, yadm_y):
        """Run without any command"""
        run = runner(command=yadm_y())
        run.report()
        assert run.code == 1
        assert run.out.startswith('Usage: yadm')

    def test_help_command(self, runner, yadm_y):
        """Run with help command"""
        run = runner(command=yadm_y('help'))
        run.report()
        assert run.code == 1
        assert run.out.startswith('Usage: yadm')
