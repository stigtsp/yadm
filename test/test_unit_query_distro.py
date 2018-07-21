"""Unit tests: query_distro"""
import sys
import pytest


@pytest.mark.skipif(
    sys.platform == 'darwin',
    reason='lsb_release not avilable on darwin')
def test_lsb_release_present(runner, yadm, distro):
    """Match lsb_release -si when present"""
    script = """
        YADM_TEST=1 source %s
        query_distro
    """ % (yadm)
    run = runner(command=['bash'], inp=script)
    print script
    run.report()
    assert run.success
    assert run.out.rstrip() == distro


def test_lsb_release_missing(runner, yadm):
    """Empty value when missing"""
    script = """
        YADM_TEST=1 source %s
        LSB_RELEASE_PROGRAM="missing_lsb_release"
        query_distro
    """ % (yadm)
    run = runner(command=['bash'], inp=script)
    print script
    run.report()
    assert run.success
    assert run.out.rstrip() == ''
