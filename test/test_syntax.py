import pytest


class Test_Syntax(object):
    """Syntax"""

    def test_syntax(self, runner, yadm):
        """Is syntactically valid"""
        run = runner(command=['bash', '-n', yadm])
        run.report()
        assert run.success

    def test_shellcheck(self, runner, yadm, shellcheck_version):
        """Passes shellcheck"""
        run = runner(command=['shellcheck', '-V'])
        if 'version: %s' % shellcheck_version not in run.out:
            pytest.skip('Unsupported shellcheck version')
        run = runner(command=['shellcheck', '-s', 'bash', yadm])
        run.report()
        assert run.success
