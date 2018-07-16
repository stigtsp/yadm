import os
import pytest
from subprocess import Popen, PIPE


class Runner:
    """Class for running commands"""

    def __init__(
            self,
            command=[],
            inp=None,
            shell=False,
            cwd=None,
            label=None):
        self.label = label
        self.command = command
        self.inp = inp
        process = Popen(
            self.command,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            shell=shell,
            cwd=cwd
        )
        (self.out, self.err) = process.communicate(input=inp)
        self.code = process.wait()
        self.success = self.code == 0
        self.failure = self.code != 0

    def __repr__(self):
        if self.label:
            return 'CMD(%s)' % self.label
        else:
            return 'CMD%s' % str(self.command)

    def report(self):
        print '%s' % self
        print '  code:%s' % self.code
        print '  stdout:%s' % self.out
        print '  stderr:%s' % self.err


@pytest.fixture(scope='session')
def runner():
    """Class for running commands"""
    return Runner


@pytest.fixture(scope='session')
def yadm():
    """Path to yadm program to be tested"""
    full_path = os.path.realpath('yadm')
    assert os.path.isfile(full_path), "yadm program file isn't present"
    return full_path


@pytest.fixture(scope='session')
def dir_root(tmpdir_factory):
    """Root directory for all test data"""
    return tmpdir_factory.getbasetemp()


@pytest.fixture(scope='session')
def dir_home(dir_root):
    """Home directory"""
    return dir_root.join('home')


@pytest.fixture(scope='session')
def dir_yadm(dir_home):
    """yadm directory"""
    return dir_home.join('.yadm')


@pytest.fixture(scope='session')
def dir_repo(dir_yadm):
    """Repo directory"""
    return dir_yadm.join('repo.git')


@pytest.fixture(scope='session')
def yadm_y(yadm, dir_yadm):
    """Function to produce params for running yadm with -Y"""
    def command_list(*args):
        return [yadm, '-Y', str(dir_yadm)] + list(args)
    return command_list


@pytest.fixture(scope='session')
def distro(runner):
    """Distro of test system"""
    run = runner(command=['lsb_release', '-si'])
    return run.out.rstrip()
