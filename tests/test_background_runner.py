"""tools/background_runner.py -- exercises real subprocess detachment, output
capture, and cross-process exit-code retrieval, since the whole point of the
tool is process/OS behavior that doesn't mean much mocked out."""
import sys
import time

from tools.background_runner import is_alive, poll_status, start_background, wait_for_exit


def test_start_captures_all_output_from_the_first_byte(tmp_path):
    log_path = tmp_path / "out.log"
    status_path = tmp_path / "out.status"
    cmd = [sys.executable, "-c", "print('line1'); print('line2')"]

    result = start_background(cmd, str(log_path), str(status_path))
    wait_result = wait_for_exit(str(status_path), poll_interval=0.05, timeout=10)

    assert wait_result["exited"] is True
    assert wait_result["exit_code"] == 0
    assert log_path.read_text() == "line1\nline2\n"
    assert result["pid"] > 0


def test_wait_retrieves_real_exit_code_from_a_separate_process_view(tmp_path):
    log_path = tmp_path / "out.log"
    status_path = tmp_path / "out.status"
    cmd = [sys.executable, "-c", "import sys; sys.exit(7)"]

    start_background(cmd, str(log_path), str(status_path))
    # wait_for_exit never touches the Popen object start_background made --
    # it only reads the status file, exactly as a later, unrelated tool call
    # would have to.
    result = wait_for_exit(str(status_path), poll_interval=0.05, timeout=10)

    assert result["exited"] is True
    assert result["exit_code"] == 7


def test_wait_times_out_while_child_still_running(tmp_path):
    log_path = tmp_path / "out.log"
    status_path = tmp_path / "out.status"
    cmd = [sys.executable, "-c", "import time; time.sleep(2)"]

    start_result = start_background(cmd, str(log_path), str(status_path))
    result = wait_for_exit(str(status_path), poll_interval=0.05, timeout=0.2)

    assert result["exited"] is False
    assert result["exit_code"] is None
    assert is_alive(start_result["pid"])

    # drain it so the test doesn't leak a live process
    wait_for_exit(str(status_path), poll_interval=0.05, timeout=10)


def test_start_survives_regardless_of_when_the_status_file_is_checked(tmp_path):
    log_path = tmp_path / "out.log"
    status_path = tmp_path / "out.status"
    cmd = [sys.executable, "-c", "import time; time.sleep(0.2)"]

    start_background(cmd, str(log_path), str(status_path))

    assert poll_status(str(status_path)) is None  # still running
    time.sleep(0.6)
    assert poll_status(str(status_path)) == 0  # finished on its own


def test_start_removes_a_stale_status_file_from_a_previous_run(tmp_path):
    log_path = tmp_path / "out.log"
    status_path = tmp_path / "out.status"
    status_path.write_text("99")

    start_background([sys.executable, "-c", "pass"], str(log_path), str(status_path))
    result = wait_for_exit(str(status_path), poll_interval=0.05, timeout=10)

    assert result["exit_code"] == 0  # not the stale 99


def test_is_alive_true_while_child_is_running(tmp_path):
    log_path = tmp_path / "out.log"
    status_path = tmp_path / "out.status"
    cmd = [sys.executable, "-c", "import time; time.sleep(2)"]

    start_result = start_background(cmd, str(log_path), str(status_path))
    try:
        assert is_alive(start_result["pid"])
    finally:
        # drain it so the test doesn't leak a live process
        wait_for_exit(str(status_path), poll_interval=0.05, timeout=10)
