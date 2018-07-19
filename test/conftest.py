import collections
import distutils.dir_util
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
def config_git(runner):
    """Configure global git configuration, if missing"""
    print 'CONFIG-GIT-GLOBAL'
    runner(command=[
        'bash',
        '-c',
        'git config user.name || '
        'git config --global user.name "test"',
        ])
    runner(command=[
        'bash',
        '-c',
        'git config user.email || '
        'git config --global user.email "test@test.test"',
        ])
    return None


@pytest.fixture(scope='session')
def yadm():
    """Path to yadm program to be tested"""
    full_path = os.path.realpath('yadm')
    assert os.path.isfile(full_path), "yadm program file isn't present"
    return full_path


@pytest.fixture()
def paths(tmpdir, yadm):
    """Function scoped test paths"""
    dir_root = tmpdir.mkdir('root')
    dir_work = dir_root.mkdir('work')
    dir_yadm = dir_root.mkdir('yadm')
    dir_repo = dir_yadm.mkdir('repo.git')
    file_config = dir_yadm.join('config')
    file_bootstrap = dir_yadm.join('bootstrap')
    Paths = collections.namedtuple(
        'Paths', [
            'pgm',
            'root',
            'work',
            'yadm',
            'repo',
            'config',
            'bootstrap',
            ])
    return Paths(
        yadm,
        dir_root,
        dir_work,
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
def dataset_one(tmpdir_factory, runner):
    """A set of test data, worktree & repo"""
    config_git(runner)
    print 'CREATING GLOBAL DATASET1'
    data = tmpdir_factory.mktemp('ds1')

    work = data.mkdir('work')
    for path in ['f1']:
        work.join(path).write(path, ensure=True)

    repo = data.mkdir('repo.git')
    env = os.environ.copy()
    env['GIT_DIR'] = str(repo)
    runner(
        command=['git', 'init', '--shared=0600', '--bare', str(repo)])
    runner(
        command=['git', 'config', 'core.bare', 'false'],
        env=env)
    runner(
        command=['git', 'config', 'status.showUntrackedFiles', 'no'],
        env=env)
    runner(
        command=['git', 'config', 'yadm.managed', 'true'],
        env=env)
    runner(
        command=['git', 'commit', '--allow-empty', '-m', 'Initial commit'],
        env=env)

    Dataset = collections.namedtuple('Dataset', ['work', 'repo'])
    return Dataset(work, repo)


@pytest.fixture()
def worktree1(dataset_one, paths):
    """Function scoped copy of ds1.work"""
    print "COPY DS1.work"
    distutils.dir_util.copy_tree(str(dataset_one.work), str(paths.work))
    return None


@pytest.fixture()
def repo1(runner, dataset_one, paths):
    """Function scoped copy of ds1.repo"""
    print "COPY DS1.repo"
    distutils.dir_util.copy_tree(str(dataset_one.repo), str(paths.repo))
    env = os.environ.copy()
    env['GIT_DIR'] = str(paths.repo)
    runner(
        command=['git', 'config', 'core.worktree', str(paths.work)],
        env=env)
    return None


@pytest.fixture()
def ds1(worktree1, repo1):
    """Function scoped copy of ds1"""
    return None


@pytest.fixture(scope='session')
def distro(runner):
    """Distro of test system"""
    run = runner(command=['lsb_release', '-si'])
    return run.out.rstrip()
