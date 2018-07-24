"""Test list"""
import os
import re
import pytest


pytestmark = pytest.mark.usefixtures('ds1')


@pytest.mark.parametrize(
    'location', [
        'work',
        'outside',
        'subdir',
    ])
def test_list(runner, yadm_y, paths, ds1_files, location):
    """List tests"""
    if location == 'work':
        run_dir = paths.work
    elif location == 'outside':
        run_dir = paths.work.join('..')
    elif location == 'subdir':
        # find first directory with tracked data
        for _ in ds1_files:
            if _.tracked:
                dirname = re.findall(r'^[^/]+/', _.path)
                if dirname:
                    run_dir = paths.work.join(dirname[0])
                    break
    with run_dir.as_cwd():
        # test with '-a'
        # should get all tracked files, relative to the work path
        run = runner(command=yadm_y('list', '-a'))
        run.report()
        returned_files = set(run.out.splitlines())
        expected_files = set([_.path for _ in ds1_files if _.tracked])
        assert returned_files == expected_files
        # test without '-a'
        # should get all tracked files, relative to the work path unless in a
        # subdir, then those should be a limited set of files, relative to the
        # subdir
        run = runner(command=yadm_y('list'))
        run.report()
        returned_files = set(run.out.splitlines())
        if location == 'subdir':
            basepath = os.path.basename(os.getcwd())
            # only expect files within the subdir
            # names should be relative to subdir
            expected_files = set(
                [_.path[len(basepath)+1:] for _ in ds1_files
                 if _.tracked and _.path.startswith(basepath)])
        assert returned_files == expected_files
