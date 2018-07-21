"""Syntax checks"""

import os
import pytest


def test_syntax(runner, yadm):
    """Is syntactically valid"""
    run = runner(command=['bash', '-n', yadm])
    print run.out
    print run.err
    assert run.success


def test_shellcheck(runner, yadm, shellcheck_version):
    """Passes shellcheck"""
    run = runner(command=['shellcheck', '-V'])
    if 'version: %s' % shellcheck_version not in run.out:
        pytest.skip('Unsupported shellcheck version')
    run = runner(command=['shellcheck', '-s', 'bash', yadm])
    print run.out
    print run.err
    assert run.success


def test_pylint(runner, pylint_version):
    """Passes pylint"""
    run = runner(command=['pylint', '--version'])
    if 'pylint %s' % pylint_version not in run.out:
        pytest.skip('Unsupported pylint version')
    pyfiles = list()
    for _ in os.listdir('test'):
        if _.endswith('.py'):
            pyfiles.append('test/%s' % _)
    run = runner(command=['pylint'] + pyfiles)
    print run.out
    print run.err
    assert run.success


def test_flake8(runner, flake8_version):
    """Passes flake8"""
    run = runner(command=['flake8', '--version'])
    if not run.out.startswith(flake8_version):
        pytest.skip('Unsupported flake8 version')
    run = runner(command=['flake8', 'test'])
    print run.out
    print run.err
    assert run.success
