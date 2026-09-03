from unittest.mock import Mock
import requests
import depotwatch

def test_heavy_shipments_filters_and_sorts_descending():
    shipments = [
        {"id": 1, "weight_kg": 50},
        {"id": 2, "weight_kg": 150},
        {"id": 3, "weight_kg": 300},
    ]

    result = depotwatch.heavy_shipments(shipments, threshold_kg=100)

    assert result == [
        {"id": 3, "weight_kg": 300},
        {"id": 2, "weight_kg": 150},
    ]

def test_heavy_shipments_excludes_unweighed():
    shipments = [
        {"id": 1, "weight_kg": 200},
        {"id": 2},                    
        {"id": 3, "weight_kg": None}, 
    ]

    result = depotwatch.heavy_shipments(shipments, threshold_kg=100)

    assert result == [
        {"id": 1, "weight_kg": 200},
    ]

def test_heavy_shipments_includes_exact_threshold():
    shipments = [{"id": 1, "weight_kg": 100}]
    result = depotwatch.heavy_shipments(shipments, threshold_kg=100)
    assert result == [{"id": 1, "weight_kg": 100}]

def test_unweighed_returns_ids_without_valid_weight():
    shipments = [
        {"id": 1, "weight_kg": 200},
        {"id": 2},
        {"id": 3, "weight_kg": None},
    ]

    result = depotwatch.unweighed(shipments)

    assert result == [2,3]

def test_unweighed_returns_empty_when_all_weighed():
    shipments = [
        {"id": 1, "weight_kg": 200},
        {"id": 2, "weight_kg": 50},
    ]

    result = depotwatch.unweighed(shipments)

    assert result == []

def test_describe_formats():
    shipment = {"id": 3, "destination": "east", "packing": "crated", "weight_kg": 310}

    result = depotwatch.describe(shipment)

    assert result == "#3 east   crated    310kg"

def test_report_prints_heavy_shipments_on_success(capsys, monkeypatch):
    fake_shipments = [
        {"id": 1, "destination": "north", "packing": "crated", "weight_kg": 120},
        {"id": 2, "destination": "east", "packing": "boxed", "weight_kg": 50},
    ]

    fake_response = Mock()
    fake_response.json.return_value = fake_shipments
    fake_response.raise_for_status.return_value = None

    monkeypatch.setattr(
        depotwatch.requests, "get",
        lambda url, timeout=None: fake_response
    )

    result = depotwatch.report(threshold_kg=100)
    captured = capsys.readouterr()

    assert result == 0
    assert "#1 north  crated    120kg" in captured.out

def test_report_prints_error_on_http_error(capsys, monkeypatch):
    fake_response = Mock()
    fake_response.status_code = 500
    
    http_error = requests.HTTPError("server error")
    http_error.response = fake_response
    
    def fake_get(url, timeout=None):
        raise http_error
    
    monkeypatch.setattr(depotwatch.requests, "get", fake_get)

    result = depotwatch.report(threshold_kg=100)
    captured = capsys.readouterr()

    assert result == 1
    assert "the depot answered with an error" in captured.out

def test_report_prints_error_when_depot_unreachable(capsys, monkeypatch):
    def fake_get(url, timeout=None):
        raise requests.ConnectionError("connection refused")
    monkeypatch.setattr(depotwatch.requests, "get", fake_get)
    result = depotwatch.report(threshold_kg=100)
    captured = capsys.readouterr()
    assert result == 1
    assert "could not reach the depot: ConnectionError" in captured.out