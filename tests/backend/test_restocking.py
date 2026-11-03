"""
Tests for restocking endpoints (recommendations and submitted orders).
"""
from datetime import datetime

import pytest

import main


@pytest.fixture(autouse=True)
def clear_submitted_orders():
    """Submitted orders live in memory, so reset them around every test."""
    main.submitted_orders.clear()
    yield
    main.submitted_orders.clear()


def get_recommendations(client, budget):
    response = client.get(f"/api/restocking/recommendations?budget={budget}")
    assert response.status_code == 200
    return response.json()


def get_max_budget(client):
    return get_recommendations(client, 0)["max_budget"]


class TestRestockRecommendations:
    """Test suite for budget-based restock recommendations."""

    def test_response_structure(self, client):
        """Test that recommendations have the expected shape."""
        data = get_recommendations(client, 1000)

        assert set(data.keys()) == {"budget", "max_budget", "total", "items"}
        assert data["budget"] == 1000
        for item in data["items"]:
            for field in ["sku", "name", "trend", "gap", "unit_cost",
                          "lead_time_days", "recommended_qty", "line_total"]:
                assert field in item

    def test_total_within_budget(self, client):
        """Test that the recommended total never exceeds the budget."""
        max_budget = get_max_budget(client)
        for budget in [50, 500, 1000, 2500, max_budget / 2]:
            data = get_recommendations(client, budget)
            assert data["total"] <= budget
            assert data["total"] == pytest.approx(sum(i["line_total"] for i in data["items"]))

    def test_sorted_by_gap(self, client):
        """Test that items are ranked by demand gap, largest first."""
        data = get_recommendations(client, get_max_budget(client))
        gaps = [item["gap"] for item in data["items"]]
        assert gaps == sorted(gaps, reverse=True)

    def test_only_last_item_partial(self, client):
        """Test that every item except the last covers its full gap."""
        data = get_recommendations(client, 2500)
        items = data["items"]
        assert len(items) > 0

        for item in items[:-1]:
            assert item["recommended_qty"] == item["gap"]
        assert 0 < items[-1]["recommended_qty"] <= items[-1]["gap"]

    def test_line_totals_match_quantities(self, client):
        """Test that each line total equals quantity times unit cost."""
        data = get_recommendations(client, 2000)
        for item in data["items"]:
            assert item["line_total"] == pytest.approx(item["recommended_qty"] * item["unit_cost"])

    def test_zero_budget_returns_no_items(self, client):
        """Test that a zero budget recommends nothing."""
        data = get_recommendations(client, 0)
        assert data["items"] == []
        assert data["total"] == 0
        assert data["max_budget"] > 0

    def test_full_budget_covers_every_gap(self, client):
        """Test that a budget at max_budget covers all growing items in full."""
        max_budget = get_max_budget(client)
        data = get_recommendations(client, max_budget)

        demand = client.get("/api/demand").json()
        growing = [f for f in demand if f["forecasted_demand"] > f["current_demand"]]

        assert len(data["items"]) == len(growing)
        assert all(i["recommended_qty"] == i["gap"] for i in data["items"])
        assert data["total"] == pytest.approx(max_budget)

    def test_excludes_non_growing_demand(self, client):
        """Test that items with flat or falling demand are never recommended."""
        data = get_recommendations(client, get_max_budget(client) * 10)
        assert all(item["gap"] > 0 for item in data["items"])
        assert "MTR-304" not in [item["sku"] for item in data["items"]]

    def test_negative_budget_rejected(self, client):
        """Test that a negative budget returns 400."""
        response = client.get("/api/restocking/recommendations?budget=-1")
        assert response.status_code == 400


class TestRestockOrders:
    """Test suite for submitting and listing restocking orders."""

    def test_no_orders_initially(self, client):
        """Test that the order list starts empty."""
        response = client.get("/api/restocking/orders")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_order(self, client):
        """Test submitting a valid order."""
        payload = {"budget": 1000, "items": [{"sku": "WDG-001", "quantity": 10}]}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["status"] == "Submitted"
        assert order["order_number"].startswith("RST-")
        assert order["total_value"] == pytest.approx(10 * 12.50)
        assert order["items"][0]["name"] == "Industrial Widget Type A"

    def test_created_order_is_listed(self, client):
        """Test that submitted orders appear in the list, newest first."""
        first = client.post("/api/restocking/orders",
                            json={"budget": 1000, "items": [{"sku": "WDG-001", "quantity": 1}]}).json()
        second = client.post("/api/restocking/orders",
                             json={"budget": 1000, "items": [{"sku": "GSK-203", "quantity": 1}]}).json()

        listed = client.get("/api/restocking/orders").json()
        assert [o["order_number"] for o in listed] == [second["order_number"], first["order_number"]]

    def test_lead_time_is_slowest_line(self, client):
        """Test that order lead time is the maximum lead time of its items."""
        payload = {"budget": 5000, "items": [
            {"sku": "GSK-203", "quantity": 5},   # 5 days
            {"sku": "CTL-330", "quantity": 1},   # 18 days
            {"sku": "FLT-405", "quantity": 5},   # 7 days
        ]}
        order = client.post("/api/restocking/orders", json=payload).json()
        assert order["lead_time_days"] == 18

        ordered = datetime.fromisoformat(order["order_date"])
        expected = datetime.fromisoformat(order["expected_delivery"])
        assert (expected - ordered).days == 18

    def test_server_side_pricing(self, client):
        """Test that the server prices the order from forecast data and ignores client prices."""
        payload = {"budget": 1000, "items": [{"sku": "WDG-001", "quantity": 4, "unit_price": 0.01}]}
        order = client.post("/api/restocking/orders", json=payload).json()
        assert order["items"][0]["unit_price"] == 12.50
        assert order["total_value"] == pytest.approx(50.0)

    def test_over_budget_rejected(self, client):
        """Test that an order above its budget returns 400 and is not stored."""
        payload = {"budget": 100, "items": [{"sku": "MTR-304", "quantity": 1}]}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 400
        assert client.get("/api/restocking/orders").json() == []

    def test_empty_items_rejected(self, client):
        """Test that an order without items returns 400."""
        response = client.post("/api/restocking/orders", json={"budget": 100, "items": []})
        assert response.status_code == 400

    def test_unknown_sku_rejected(self, client):
        """Test that an unknown SKU returns 400."""
        payload = {"budget": 1000, "items": [{"sku": "NOPE-999", "quantity": 1}]}
        response = client.post("/api/restocking/orders", json=payload)
        assert response.status_code == 400

    def test_non_positive_quantity_rejected(self, client):
        """Test that zero or negative quantities return 400."""
        for qty in [0, -5]:
            payload = {"budget": 1000, "items": [{"sku": "WDG-001", "quantity": qty}]}
            response = client.post("/api/restocking/orders", json=payload)
            assert response.status_code == 400

    def test_restock_orders_do_not_affect_orders(self, client):
        """Test that submitted restock orders stay out of the regular orders list."""
        before = len(client.get("/api/orders").json())
        client.post("/api/restocking/orders", json={"budget": 1000, "items": [{"sku": "WDG-001", "quantity": 1}]})
        assert len(client.get("/api/orders").json()) == before


class TestDemandForecastCostFields:
    """Test that demand forecasts expose the new pricing fields."""

    def test_demand_includes_cost_and_lead_time(self, client):
        """Test that every forecast has a positive unit cost and lead time."""
        response = client.get("/api/demand")
        assert response.status_code == 200
        for forecast in response.json():
            assert forecast["unit_cost"] > 0
            assert forecast["lead_time_days"] > 0
