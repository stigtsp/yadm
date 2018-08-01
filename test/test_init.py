"""Test init"""

import pytest


@pytest.mark.parametrize(
    'alt_work, repo_present, force', [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (False, True, True),
        (True, True, True),
    ], ids=[
        'simple',
        '-w',
        'existing repo',
        '-f',
        '-w & -f',
    ])
@pytest.mark.usefixtures('ds1_work_copy')
def test_init(
        runner, yadm_y, paths, repo_config, alt_work, repo_present, force):
    """Test init

    Repos should have attribs:
        - 0600 permissions
        - not bare
        - worktree = $HOME
        - showUntrackedFiles = no
        - yadm.managed = true
    """

    # these tests will assume this for $HOME
    home = str(paths.root.mkdir('HOME'))

    # ds1_work_copy comes WITH a repo present
    if not repo_present:
        paths.repo.remove()

    # command args
    args = ['init']
    if alt_work:
        args.extend(['-w', paths.work])
    if force:
        args.append('-f')

    # run init
    run = runner(yadm_y(*args), env={'HOME': home})
    run.report()

    if repo_present and not force:
        assert run.code == 1
        assert 'repo already exists' in run.out
    else:
        assert run.code == 0
        assert 'Initialized empty shared Git repository' in run.out

        if alt_work:
            assert repo_config('core.worktree') == paths.work
        else:
            assert repo_config('core.worktree') == home

        # uniform repo assertions
        assert paths.repo.stat().mode == 0o42700
        assert repo_config('core.bare') == 'false'
        assert repo_config('status.showUntrackedFiles') == 'no'
        assert repo_config('yadm.managed') == 'true'
