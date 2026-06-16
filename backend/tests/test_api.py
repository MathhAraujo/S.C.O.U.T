async def test_health_check(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_temperature_ingestion_with_and_without_assignment(client):
    athlete_response = await client.post(
        "/api/v1/athletes",
        json={
            "name": "Joao Silva",
            "birth_date": "2002-05-10",
            "position": "Midfielder",
            "team": "Team A",
        },
    )
    assert athlete_response.status_code == 201
    athlete_id = athlete_response.json()["id"]

    device_response = await client.post(
        "/api/v1/devices",
        json={"device_uid": "esp32-prototype-001", "firmware_version": "0.1.0"},
    )
    assert device_response.status_code == 201

    duplicate_device_response = await client.post(
        "/api/v1/devices",
        json={"device_uid": "esp32-prototype-001", "firmware_version": "0.1.0"},
    )
    assert duplicate_device_response.status_code == 201
    assert duplicate_device_response.json()["id"] == device_response.json()["id"]

    assignment_response = await client.post(
        "/api/v1/device-assignments",
        json={"device_uid": "esp32-prototype-001", "athlete_id": athlete_id},
    )
    assert assignment_response.status_code == 201

    measurement_response = await client.post(
        "/api/v1/telemetry/temperature",
        json={
            "device_uid": "esp32-prototype-001",
            "sensor": "NTC",
            "value_celsius": 36.7,
            "unit": "celsius",
            "firmware_version": "0.1.0",
            "uptime_ms": 125000,
        },
    )
    assert measurement_response.status_code == 201
    assert measurement_response.json()["message"] == "temperature measurement registered"

    unassigned_response = await client.post(
        "/api/v1/telemetry/temperature",
        json={
            "device_id": "esp32-unassigned",
            "sensor": "NTC",
            "value_celsius": 35.9,
            "unit": "celsius",
            "firmware_version": "0.1.0",
            "uptime_ms": 2000,
        },
    )
    assert unassigned_response.status_code == 201

    list_response = await client.get("/api/v1/telemetry/temperature?limit=100")
    assert list_response.status_code == 200
    measurements = list_response.json()
    assert len(measurements) == 2
    assert any(item["athlete_id"] == athlete_id for item in measurements)
    assert any(item["athlete_id"] is None for item in measurements)
    assert any(item["device_uid"] == "esp32-prototype-001" for item in measurements)
    assert any(item["device_uid"] == "esp32-unassigned" for item in measurements)


async def test_device_assignment_history_is_preserved(client):
    first_athlete = await client.post("/api/v1/athletes", json={"name": "First Athlete"})
    second_athlete = await client.post("/api/v1/athletes", json={"name": "Second Athlete"})
    await client.post("/api/v1/devices", json={"device_uid": "esp32-prototype-002"})

    first_assignment = await client.post(
        "/api/v1/device-assignments",
        json={"device_uid": "esp32-prototype-002", "athlete_id": first_athlete.json()["id"]},
    )
    assert first_assignment.status_code == 201

    second_assignment = await client.post(
        "/api/v1/device-assignments",
        json={"device_uid": "esp32-prototype-002", "athlete_id": second_athlete.json()["id"]},
    )
    assert second_assignment.status_code == 201

    history_response = await client.get("/api/v1/device-assignments?device_uid=esp32-prototype-002")
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 2
    assert sum(1 for item in history if item["ended_at"] is None) == 1
    assert sum(1 for item in history if item["ended_at"] is not None) == 1


async def test_temperature_payload_validation(client):
    response = await client.post(
        "/api/v1/telemetry/temperature",
        json={
            "device_uid": "esp32-prototype-001",
            "sensor": "OTHER",
            "value_celsius": 36.7,
            "unit": "celsius",
        },
    )

    assert response.status_code == 422
