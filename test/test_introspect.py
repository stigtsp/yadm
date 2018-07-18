import collections
import pytest
import re


class Test_Introspection(object):
    """Introspection"""

    Category = collections.namedtuple(
        'Category', ['name', 'code', 'count', 'regex'])

    @pytest.fixture(params=[
        Category('', 0, 0, None),
        Category('invalid', 0, 0, None),
        Category('commands', 0, 15, r'version'),
        Category('configs', 0, 13, r'yadm\.auto-alt'),
        Category('repo', 0, 1, 'MATCHREPO'),
        Category('switches', 0, 7, r'--yadm-dir'),
        ])
    def category(self, request):
        """Introspection category, and expected results for the category."""
        return request.param

    def test_introspect_category(self, runner, yadm_y, category, paths):
        """Validate introspection category"""
        if category.name:
            run = runner(command=yadm_y('introspect', category.name))
        else:
            run = runner(command=yadm_y('introspect'))
        run.report()
        assert run.code == category.code
        if category.regex == 'MATCHREPO':
            assert run.out.rstrip() == paths.repo
        elif category.regex:
            assert re.search(category.regex, run.out)
        else:
            assert run.out == ''
        assert len(run.out.split()) == category.count, (
            "unexpected number of intropected values")
