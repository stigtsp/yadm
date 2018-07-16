import pytest
import re


class Test_Version(object):
    """Version"""

    @pytest.fixture(scope='module')
    def expected_version(self, yadm):
        """
        Expected semantic version number. This is taken directly out of yadm,
        searching for the VERSION= string.
        """
        yadm_version = re.findall(
            r'VERSION=([^\n]+)',
            open(yadm).read())
        if yadm_version:
            return yadm_version[0]
        pytest.fail('version not found in %s' % yadm)

    def test_semantic_version(self, expected_version):
        """Version is semantic"""
        # semantic version conforms to MAJOR.MINOR.PATCH
        assert re.search(r'^\d+\.\d+\.\d+$', expected_version), (
                'does not conform to MAJOR.MINOR.PATCH')

    def test_reported_version(
            self, runner, yadm_y, expected_version):
        """Report correct version"""
        run = runner(command=yadm_y('version'))
        run.report()
        assert run.success
        assert run.out == 'yadm %s\n' % (expected_version)
