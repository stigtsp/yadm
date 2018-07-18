import collections
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
            env=None,
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
            cwd=cwd,
            env=env,
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


@pytest.fixture()
def paths(tmpdir, yadm):
    """Function scoped test paths"""
    Paths = collections.namedtuple(
        'Paths', [
            'pgm',
            'root',
            'home',
            'yadm',
            'repo',
            'config',
            'bootstrap',
            ])
    dir_root = tmpdir.mkdir('root')
    dir_home = dir_root.mkdir('home')
    dir_yadm = dir_home.mkdir('.yadm')
    dir_repo = dir_yadm.mkdir('repo.git')
    file_config = dir_yadm.join('config')
    file_bootstrap = dir_yadm.join('bootstrap')
    return Paths(
        yadm,
        dir_root,
        dir_home,
        dir_yadm,
        dir_repo,
        file_config,
        file_bootstrap,
        )


@pytest.fixture()
def yadm_y(paths):
    """Function to produce params for running yadm with -Y"""
    def command_list(*args):
        return [paths.pgm, '-Y', str(paths.yadm)] + list(args)
    return command_list


@pytest.fixture(scope='session')
def distro(runner):
    """Distro of test system"""
    run = runner(command=['lsb_release', '-si'])
    return run.out.rstrip()
