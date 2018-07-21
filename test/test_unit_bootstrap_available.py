"""Unit tests: bootstrap_available"""


def test_bootstrap_missing(runner, paths):
    """Test result of bootstrap_available, when bootstrap missing"""
    run_test(runner, paths, 1)


def test_bootstrap_no_exec(runner, paths):
    """Test result of bootstrap_available, when bootstrap not executable"""
    paths.bootstrap.write('')
    paths.bootstrap.chmod(0644)
    run_test(runner, paths, 1)


def test_bootstrap_exec(runner, paths):
    """Test result of bootstrap_available, when bootstrap executable"""
    paths.bootstrap.write('')
    paths.bootstrap.chmod(0775)
    run_test(runner, paths, 0)


def run_test(runner, paths, expected_code):
    """Run bootstrap_available, and test result"""
    script = """
        YADM_TEST=1 source %s
        YADM_BOOTSTRAP='%s'
        bootstrap_available
    """ % (paths.pgm, paths.bootstrap)
    run = runner(command=['bash'], inp=script)
    print script
    run.report()
    assert run.code == expected_code
