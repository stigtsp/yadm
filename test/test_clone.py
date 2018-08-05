"""Test clone"""
import pytest

BOOTSTRAP_MSG = 'Bootstrap successful'
BOOTSTRAP_CODE = 123


@pytest.mark.usefixtures('remote')
@pytest.mark.parametrize(
    'good_remote, repo_exists, force, conflicts', [
        (False, False, False, False),
        (True, False, False, False),
        (True, True, False, False),
        (True, True, True, False),
        (True, False, False, True),
    ], ids=[
        'bad remote',
        'simple',
        'existing repo',
        '-f',
        'conflicts',
    ])
def test_clone(
        runner, paths, yadm_y, repo_config, ds1,
        good_remote, repo_exists, force, conflicts):
    """Test basic clone operation"""

    # determine remote url
    remote_url = f'file://{paths.remote}'
    if not good_remote:
        remote_url = 'file://bad_remote'

    old_repo = None
    if repo_exists:
        # put a repo in the way
        paths.repo.mkdir()
        old_repo = paths.repo.join('old_repo')
        old_repo.write('old_repo')

    if conflicts:
        ds1.tracked[0].relative.write('conflict')
        assert ds1.tracked[0].relative.exists()

    # run the clone command
    args = ['clone', '-w', paths.work]
    if force:
        args += ['-f']
    args += [remote_url]
    run = runner(command=yadm_y(*args))
    run.report()

    if not good_remote:
        # clone should fail
        assert run.code == 1
        assert 'Unable to fetch origin' in run.out
        assert not paths.repo.exists()
    elif repo_exists and not force:
        # can't overwrite data
        assert run.code == 1
        assert 'Git repo already exists' in run.out
    else:
        # clone should succeed, and repo should be configured properly
        assert successful_clone(run, paths, repo_config)

        # ensure conflicts are handled properly
        if conflicts:
            assert 'NOTE' in run.out
            assert 'Merging origin/master failed' in run.out
            assert 'Conflicts preserved' in run.out

        # confirm correct Git origin
        run = runner(
            command=('git', 'remote', '-v', 'show'),
            env={'GIT_DIR': paths.repo})
        run.report()
        assert run.code == 0
        assert f'origin\t{remote_url}' in run.out

        # ensure conflicts are really preserved
        if conflicts:
            # test to see if the work tree is actually "clean"
            run = runner(
                command=yadm_y('status', '-uno', '--porcelain'),
                cwd=paths.work)
            run.report()
            assert run.out == '', 'worktree has unexpected changes'

            # test to see if the conflicts are stashed
            run = runner(command=yadm_y('stash', 'list'), cwd=paths.work)
            run.report()
            assert 'Conflicts preserved' in run.out, 'conflicts not stashed'

            # verify content of the stashed conflicts
            run = runner(command=yadm_y('stash', 'show', '-p'), cwd=paths.work)
            run.report()
            assert '\n+conflict' in run.out, 'conflicts not stashed'

    # another force-related assertion
    if old_repo:
        if force:
            assert not old_repo.exists()
        else:
            assert old_repo.exists()


@pytest.mark.usefixtures('remote')
@pytest.mark.parametrize(
    'bs_exists, bs_param, answer', [
        (False, '--bootstrap', None),
        (True, '--bootstrap', None),
        (True, '--no-bootstrap', None),
        (True, None, 'n'),
        (True, None, 'y'),
    ], ids=[
        'force, missing',
        'force, existing',
        'prevent',
        'existing, answer n',
        'existing, answer y',
    ])
def test_clone_bootstrap(
        runner, paths, yadm_y, repo_config, bs_exists, bs_param, answer):
    """Test bootstrap clone features"""

    # establish a bootstrap
    create_bootstrap(paths, bs_exists)

    # run the clone command
    args = ['clone', '-w', paths.work]
    if bs_param:
        args += [bs_param]
    args += [f'file://{paths.remote}']
    expect = []
    if answer:
        expect.append(('Would you like to execute it now', answer))
    run = runner(command=yadm_y(*args), expect=expect)
    run.report()

    if answer:
        assert 'Would you like to execute it now' in run.out

    expected_code = 0
    if bs_exists and bs_param != '--no-bootstrap':
        expected_code = BOOTSTRAP_CODE

    if answer == 'y':
        expected_code = BOOTSTRAP_CODE
        assert BOOTSTRAP_MSG in run.out
    elif answer == 'n':
        expected_code = 0
        assert BOOTSTRAP_MSG not in run.out

    assert successful_clone(run, paths, repo_config, expected_code)

    if not bs_exists:
        assert BOOTSTRAP_MSG not in run.out


def create_bootstrap(paths, exists):
    """Create bootstrap file for test"""
    if exists:
        paths.bootstrap.write(
            '#!/bin/sh\n'
            f'echo {BOOTSTRAP_MSG}\n'
            f'exit {BOOTSTRAP_CODE}\n')
        paths.bootstrap.chmod(0o775)
        assert paths.bootstrap.exists()
    else:
        assert not paths.bootstrap.exists()


# "Command 'clone' (local insecure .ssh and .gnupg data, no rltd data in repo)"
# "Command 'clone' (local insecure .gnupg data, related data in repo)"
# "Command 'clone' (local insecure .ssh data, related data in repo)"
# "Command 'clone' (no existing .gnupg, .gnupg data tracked in repo)"
# "Command 'clone' (no existing .ssh, .ssh data tracked in repo)"
def test_clone_perms():
    """Test clone permission related functions"""
    pytest.skip('Not implemented')


def successful_clone(run, paths, repo_config, expected_code=0):
    """Assert clone is successful"""
    assert run.code == expected_code
    assert 'Initialized' in run.out
    assert paths.repo.stat().mode == 0o42700
    assert repo_config('core.bare') == 'false'
    assert repo_config('status.showUntrackedFiles') == 'no'
    assert repo_config('yadm.managed') == 'true'
    return True


@pytest.fixture()
def remote(paths, ds1_repo_copy):
    """Function scoped remote (based on ds1)"""
    # pylint: disable=unused-argument
    # This is ignored because
    # @pytest.mark.usefixtures('ds1_remote_copy')
    # cannot be applied to another fixture.
    paths.remote.remove()
    paths.repo.move(paths.remote)
    return None
