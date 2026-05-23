# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Equipo pre.voto
import pytest


@pytest.mark.usefixtures("seed_data")
class TestCountriesRouter:

    async def test_list_countries(self, client):
        resp = await client.get("/countries")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        co = next(c for c in data if c["code"] == "xt")
        assert co["name"] == "Testlandia"
        assert co["is_active"] is True
        assert co["next_election"] is not None
        assert co["next_election"]["type"] == "presidential_r1"

    async def test_get_country_by_code(self, client):
        resp = await client.get("/countries/xt")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == "xt"
        assert data["name"] == "Testlandia"
        assert len(data["elections"]) >= 1

    async def test_get_country_not_found(self, client):
        resp = await client.get("/countries/zz")
        assert resp.status_code == 404
        assert "error" in resp.json()

    async def test_get_country_case_insensitive(self, client):
        resp = await client.get("/countries/XT")
        assert resp.status_code == 200
        assert resp.json()["code"] == "xt"
