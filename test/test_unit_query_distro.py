class Test_Unit_Query_Distro(object):
    """Unit tests: query_distro"""

    def test_lsb_release_present(self, runner, yadm, distro):
        """Match lsb_release -si when present"""
        script = """
            YADM_TEST=1 source %s
            query_distro
        """ % (yadm)
        run = runner(command=['bash'], inp=script)
        print script
        run.report()
        assert run.success
        assert run.out.rstrip() == distro

    def test_lsb_release_missing(self, runner, yadm):
        """Empty value when missing"""
        script = """
            YADM_TEST=1 source %s
            LSB_RELEASE_PROGRAM="missing_lsb_release"
            query_distro
        """ % (yadm)
        run = runner(command=['bash'], inp=script)
        print script
        run.report()
        assert run.success
        assert run.out.rstrip() == ''
