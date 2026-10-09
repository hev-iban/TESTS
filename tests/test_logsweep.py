from logsweep import sweep
import logsweep

def test_sweep_no_log_files_prints_message_and_returns_zero(tmp_path, capsys):
    result = logsweep.sweep(str(tmp_path))

    captured = capsys.readouterr()

    assert result == 0
    assert "no log files here" in captured.out

def test_sweep_non_log_files_are_ignored(tmp_path, capsys):
    (tmp_path / "notes.txt").write_text("this is not a log\n")
    (tmp_path / "a.log").write_text("INFO hello\n")

    result = logsweep.sweep(str(tmp_path))
    captured = capsys.readouterr()

    assert "notes.txt" not in captured.out
    assert "a.log" in captured.out
    assert result == 0

def test_sweep_counts_info_warn_error_correctly(tmp_path, capsys):
    (tmp_path / "a.log").write_text(
        "INFO one\n"
        "INFO two\n"
        "WARN three\n"
        "ERROR four\n"
        "ERROR five\n"
    )

    result = logsweep.sweep(str(tmp_path))
    captured = capsys.readouterr()

    assert "2 info" in captured.out
    assert "1 warn" in captured.out
    assert "2 error" in captured.out
    assert result == 2

def test_sweep_files_processed_in_sorted_order(tmp_path, capsys):
    (tmp_path / "z.log").write_text("INFO first created\n")
    (tmp_path / "a.log").write_text("INFO second created\n")
    logsweep.sweep(str(tmp_path))
    captured = capsys.readouterr()
    a_pos = captured.out.find("a.log")
    z_pos = captured.out.find("z.log")
    assert a_pos < z_pos

def test_sweep_worst_file_is_the_one_with_most_errors(tmp_path, capsys):
    (tmp_path / "a.log").write_text("ERROR one\n")
    (tmp_path / "b.log").write_text("ERROR one\nERROR two\nERROR three\n")

    logsweep.sweep(str(tmp_path))
    captured = capsys.readouterr()

    assert "worst file: b.log" in captured.out

def test_sweep_worst_file_tie_goes_to_first_alphabetically(tmp_path, capsys):
    (tmp_path / "a.log").write_text("ERROR one\nERROR two\n")
    (tmp_path / "b.log").write_text("ERROR one\nERROR two\n")

    logsweep.sweep(str(tmp_path))
    captured = capsys.readouterr()

    assert "worst file: a.log" in captured.out
    assert "worst file: b.log" not in captured.out

def test_sweep_no_worst_file_line_when_all_zero_errors(tmp_path, capsys):
    (tmp_path / "a.log").write_text("INFO fine\n")
    (tmp_path / "b.log").write_text("WARN careful\n")

    logsweep.sweep(str(tmp_path))
    captured = capsys.readouterr()

    assert "worst file: " not in captured.out

def test_sweep_total_errors_summed_across_files(tmp_path):
    (tmp_path / "a.log").write_text("ERROR one\nERROR two\n")
    (tmp_path / "b.log").write_text("ERROR one\n")

    result = logsweep.sweep(str(tmp_path))

    assert result == 3

def test_sweep_line_prefix_matching_is_startswith_not_exact(tmp_path, capsys):
    (tmp_path / "a.log").write_text("INFOX something weird\n")

    logsweep.sweep(str(tmp_path))
    captured = capsys.readouterr()

    assert "1 info" in captured.out