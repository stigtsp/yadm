class Test_Unit_Bootstrap_Available(object):
    """Unit tests: bootstrap_available"""

    def test_bootstrap_missing(self, runner, paths):
        """Test result of bootstrap_available, when bootstrap missing"""
        self.run_test(runner, paths, 1)

    def test_bootstrap_no_exec(self, runner, paths):
        """Test result of bootstrap_available, when bootstrap not executable"""
        paths.bootstrap.write('')
        paths.bootstrap.chmod(0644)
        self.run_test(runner, paths, 1)

    def test_bootstrap_exec(self, runner, paths):
        """Test result of bootstrap_available, when bootstrap executable"""
        paths.bootstrap.write('')
        paths.bootstrap.chmod(0775)
        self.run_test(runner, paths, 0)

    def run_test(self, runner, paths, expected_code):
        """Run bootstrap_available, and test result"""
        script = """
            YADM_TEST=1 source %s
            YADM_BOOTSTRAP='%s'
            ls -l $YADM_BOOTSTRAP
            bootstrap_available
        """ % (paths.pgm, paths.bootstrap)
        run = runner(command=['bash'], inp=script)
        print script
        run.report()
        assert run.code == expected_code
