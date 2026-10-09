from receipt import billable_units, line_cost_pence, discount_pence, format_pence,parse_line,parse_manifest,total_pence, render
import pytest

def test_billable_units_is_not_rounded_up():
    assert billable_units(50) == 2

def test_billable_units_is_rounded_up_with_remainder():
    assert billable_units(55) == 3
    
def  test_billable_units_is_less_than_zero():
    with pytest.raises(ValueError):
        billable_units(-1)

def  test_billable_units_is_zero():
    with pytest.raises(ValueError):
        billable_units(0)


def test_line_cost_pence_is_created():
    assert line_cost_pence("crated", 30) == 700

def test_line_cost_pence_is_loose():
    assert line_cost_pence("loose", 75) == 825


def test_discount_pence_no_discount():
    assert discount_pence(1500, 0) == 0

def test_discount_pence_at_boundary():
    assert discount_pence(525, 10) == 26

def test_discount_pence__discounted():
    assert discount_pence(2000, 15) == 100


def test_format_pence_clean_case():
    assert format_pence(800) == "8.00"

def test_format_pence_digit_case():
    assert format_pence(850) == "8.50"

def test_format_pence_negative_case():
    assert format_pence(-700) == "-7.00"

def test_parse_line_good_parts_count():
    assert parse_line("north,   crated, 100") == ("north", "crated", 100.0)

def test_parse_line_wrong_parts_count():
    with pytest.raises(ValueError):
        parse_line("north,   crated, 100, 130")

def test_parse_line_destination_empty():
    with pytest.raises(ValueError):
        parse_line(", crated, 100")

def test_parse_line_unknown_packing():
    with pytest.raises(ValueError):
        parse_line("north,  packer, 100")

def test_parse_line_invalid_weight():
    with pytest.raises(ValueError):
        parse_line("north,   crated, abc")


def test_parse_manifest_clean():
    text = """north, crated, 100
south, loose, 50"""
    assert parse_manifest(text) == [("north", "crated", 100.0), ("south", "loose", 50.0)]

def test_parse_manifest_skips_blanks_and_comments():
    text = """# comment
north, crated, 100

south, loose, 50"""
    assert parse_manifest(text) == [("north", "crated", 100.0), ("south", "loose", 50.0)]


def test_total_pence_no_discount():
    rows = [
        ("north", "crated", 30),
        ("south", "loose", 75),
    ]
    assert total_pence(rows) == 1525

def test_total_pence_with_discount():
    rows = [("x", "loose", 25)] * 10
    assert total_pence(rows) == 2613

def test_render_formats_row_correctly():
    rows = [("north", "crated", 30)]
    expected = "%-8s %-7s %6.1fkg  %8s" % ("north", "crated", 30, "7.00")
    assert render(rows)[0] == expected
    assert render(rows)[1] == "1 rows"
    assert render(rows)[2] == "total 7.00"

def test_render_formats_multiple_rows_correctly():
    rows = [
        ("north", "crated", 30),
        ("south", "loose", 75),
    ]
    expected_0 = "%-8s %-7s %6.1fkg  %8s" % ("north", "crated", 30, "7.00")
    expected_1 = "%-8s %-7s %6.1fkg  %8s" % ("south", "loose", 75, "8.25")
    
    assert len(render(rows)) == 4
    assert render(rows)[0] == expected_0
    assert render(rows)[1] == expected_1
    assert render(rows)[2] == "2 rows"
    assert render(rows)[3] == "total 15.25"