"""Test git"""
import re
import pytest


@pytest.mark.usefixtures('ds1_copy')
def test_git(runner, yadm_y, paths):
    """Test series of passthrough git commands

    Passthru unknown commands to Git
    Git command 'add' - badfile
    Git command 'add'
    Git command 'status'
    Git command 'commit'
    Git command 'log'
    """

    # Passthru unknown commands to Git
    run = runner(command=yadm_y('bogus'))
    run.report()
    assert run.code == 1
    assert "git: 'bogus' is not a git command." in run.err
    assert "See 'git --help'" in run.err

    # Git command 'add' - badfile
    run = runner(command=yadm_y('add', '-v', 'does_not_exist'))
    run.report()
    assert run.code == 128
    assert "pathspec 'does_not_exist' did not match any files" in run.err

    # Git command 'add'
    newfile = paths.work.join('test_git')
    newfile.write('test_git')
    run = runner(command=yadm_y('add', '-v', str(newfile)))
    run.report()
    assert run.code == 0
    assert "add 'test_git'" in run.out

    # Git command 'status'
    run = runner(command=yadm_y('status'))
    run.report()
    assert run.code == 0
    assert re.search(r'new file:\s+test_git', run.out)

    # Git command 'commit'
    run = runner(command=yadm_y('commit', '-m', 'Add test_git'))
    run.report()
    assert run.code == 0
    assert '1 file changed' in run.out
    assert '1 insertion' in run.out
    assert re.search(r'create mode .+ test_git', run.out)

    # Git command 'log'
    run = runner(command=yadm_y('log', '--oneline'))
    run.report()
    assert run.code == 0
    assert 'Add test_git' in run.out
