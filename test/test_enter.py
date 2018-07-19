import os
import pytest


@pytest.mark.usefixtures('ds1')
class Test_Enter(object):
    """Enter"""

    def test_enter_shell_set(self, runner, yadm_y):
        """Enter operates if $SHELL set"""
        env = os.environ.copy()
        env['SHELL'] = '/usr/bin/env'
        run = runner(command=yadm_y('enter'), env=env)
        run.report()
        assert run.code == 0
        assert run.out.startswith('Entering yadm repo')
        assert 'GIT_DIR=' in run.out
        assert 'PROMPT=yadm shell' in run.out
        assert 'PS1=yadm shell' in run.out
        assert run.out.rstrip().endswith('Leaving yadm repo')

    def test_enter_shell_unset(self, runner, yadm_y):
        """Enter errors if $SHELL unset"""
        env = os.environ.copy()
        env['SHELL'] = ''
        run = runner(command=yadm_y('enter'), env=env)
        run.report()
        assert run.code == 1
        assert 'does not refer to an executable' in run.out

    def test_enter_shell_no_exec(self, runner, yadm_y, paths):
        """Enter errors if $SHELL not executable"""
        env = os.environ.copy()
        badshell = paths.root.join('badshell')
        badshell.write('')
        env['SHELL'] = str(badshell)
        run = runner(command=yadm_y('enter'), env=env)
        run.report()
        assert run.code == 1
        assert 'does not refer to an executable' in run.out
