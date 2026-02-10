from pathlib import Path

import pytest

from Applications.AlgorithmsLab.GradeSystem import (
    GradeSystem,
    GradeSystemDriver,
    NoStudentException,
)


def test_insert_grade_rejects_invalid_input():
    grade_system = GradeSystem()

    with pytest.raises(ValueError):
        grade_system.insert_grade("97531 DS")

    with pytest.raises(ValueError):
        grade_system.insert_grade("97531 DS 80 DM")


def test_insert_grade_rejects_non_integer_score():
    grade_system = GradeSystem()

    with pytest.raises(ValueError, match="成績必須是整數"):
        grade_system.insert_grade("97531 DS A+")


def test_save_data_persists_one_student_per_line(tmp_path):
    driver = GradeSystemDriver()
    driver.file_path = str(tmp_path / "grade2.txt")

    driver.grade_system.insert_grade("97531 DS 80 DM 81")
    driver.grade_system.insert_grade("97532 DS 90")

    driver.save_data()

    content = Path(driver.file_path).read_text(encoding="utf-8").strip().splitlines()

    assert content == ["97531 DS 80 DM 81", "97532 DS 90"]


def test_load_data_skips_blank_lines(tmp_path):
    data_file = tmp_path / "grade2.txt"
    data_file.write_text("97531 DS 80 DM 81\n\n97532 DS 90\n", encoding="utf-8")

    driver = GradeSystemDriver()
    driver.file_path = str(data_file)

    driver.load_data()

    assert driver.grade_system.search_grade("97531", "DM") == 81
    assert driver.grade_system.search_grade("97532", "DS") == 90


def test_load_data_skips_invalid_lines_and_keeps_valid_data(tmp_path, capsys):
    data_file = tmp_path / "grade2.txt"
    data_file.write_text("97531 DS 80\n97532 DS A+\n97533 DM 77\n", encoding="utf-8")

    driver = GradeSystemDriver()
    driver.file_path = str(data_file)

    driver.load_data()

    output = capsys.readouterr().out
    assert "略過無效資料" in output
    assert driver.grade_system.search_grade("97531", "DS") == 80
    assert driver.grade_system.search_grade("97533", "DM") == 77
    with pytest.raises(NoStudentException):
        driver.grade_system.search_grade("97532", "DS")
