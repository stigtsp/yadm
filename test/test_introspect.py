"""Test introspect"""
import re
import pytest


@pytest.mark.parametrize(
    'name, code, count, regex', [
        ('', 0, 0, None),
        ('invalid', 0, 0, None),
        ('commands', 0, 15, r'version'),
        ('configs', 0, 13, r'yadm\.auto-alt'),
        ('repo', 0, 1, 'MATCHREPO'),
        ('switches', 0, 7, r'--yadm-dir'),
    ], ids=[
        'none',
        'invalid',
        'commands',
        'configs',
        'repo',
        'switches',
    ])
def test_introspect_category(
        runner, yadm_y, paths, name, code, count, regex):
    """Validate introspection category"""
    if name:
        run = runner(command=yadm_y('introspect', name))
    else:
        run = runner(command=yadm_y('introspect'))
    run.report()
    assert run.code == code
    if regex == 'MATCHREPO':
        assert run.out.rstrip() == paths.repo
    elif regex:
        assert re.search(regex, run.out)
    else:
        assert run.out == ''
    assert len(run.out.split()) == count, (
        "unexpected number of intropected values")
