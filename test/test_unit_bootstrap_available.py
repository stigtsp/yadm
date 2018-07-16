class Test_Unit_Bootstrap_Available(object):
    """Unit tests: bootstrap_available"""

    def test_bootstrap_missing(self, tmpdir, runner, yadm):
        """Test result of bootstrap_available, when bootstrap missing"""
        file_bootstrap = tmpdir.join('bootstrap')
        self.run_test(runner, yadm, file_bootstrap, 1)

    def test_bootstrap_no_exec(self, tmpdir, runner, yadm):
        """Test result of bootstrap_available, when bootstrap not executable"""
        file_bootstrap = tmpdir.join('bootstrap')
        file_bootstrap.write('')
        file_bootstrap.chmod(0644)
        self.run_test(runner, yadm, file_bootstrap, 1)

    def test_bootstrap_exec(self, tmpdir, runner, yadm):
        """Test result of bootstrap_available, when bootstrap executable"""
        file_bootstrap = tmpdir.join('bootstrap')
        file_bootstrap.write('')
        file_bootstrap.chmod(0775)
        self.run_test(runner, yadm, file_bootstrap, 0)

    def run_test(self, runner, yadm, file_bootstrap, expected_code):
        """Run bootstrap_available, and test result"""
        script = """
            YADM_TEST=1 source %s
            YADM_BOOTSTRAP='%s'
            ls -l $YADM_BOOTSTRAP
            bootstrap_available
        """ % (yadm, file_bootstrap)
        run = runner(command=['bash'], inp=script)
        print script
        run.report()
        assert run.code == expected_code
