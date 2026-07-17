"""Tests unitaires pour custom_components.vacances_scolaires.calendar."""
import pytest
from datetime import datetime
from unittest.mock import MagicMock

from custom_components.vacances_scolaires.calendar import (
    convert_to_iso_format,
    VacancesScolairesCalendar,
)


# ---- convert_to_iso_format -------------------------------------------------

def test_convert_to_iso_format_valid():
    # "01 janvier 2024 à 12:00:00" -> "2024-01-01T12:00:00"
    input_str = "01 janvier 2024 à 12:00:00"
    assert convert_to_iso_format(input_str) == "2024-01-01T12:00:00"


def test_convert_to_iso_format_invalid_month():
    with pytest.raises(ValueError):
        convert_to_iso_format("01 foo 2024 à 12:00:00")


def test_convert_to_iso_format_invalid_format():
    with pytest.raises(ValueError):
        convert_to_iso_format("2024-01-01")


# ---- VacancesScolairesCalendar.event ---------------------------------------

class DummyCoordinator:
    def __init__(self, data):
        self.data = data


class DummyConfigEntry:
    def __init__(self, entry_id, title):
        self.entry_id = entry_id
        self.title = title


def test_calendar_event_when_on_vacation(monkeypatch):
    data = {
        "on_vacation": True,
        "start_date": "01 juillet 2024 à 00:00:00",
        "end_date": "15 juillet 2024 à 23:59:59",
        "location": "Paris",
        "description": "Vacances d'été",
    }
    coordinator = DummyCoordinator(data)
    config_entry = DummyConfigEntry("test", "Test")
    cal = VacancesScolairesCalendar(coordinator, config_entry)

    monkeypatch.setattr(
        "custom_components.vacances_scolaires.coordinator.get_timezone",
        lambda loc: "Europe/Paris",
    )

    from custom_components.vacances_scolaires import calendar as cal_mod

    def fake_calendar_event(**kwargs):
        obj = MagicMock()
        obj.summary = kwargs.get("summary")
        obj.start = kwargs.get("start")
        obj.end = kwargs.get("end")
        return obj

    monkeypatch.setattr(cal_mod, "CalendarEvent", fake_calendar_event)

    event = cal.event
    assert event is not None
    assert event.summary == "Vacances d'été"
    assert isinstance(event.start, datetime)
    assert isinstance(event.end, datetime)
    assert event.start.tzinfo is not None
    assert event.end.tzinfo is not None


def test_calendar_event_when_not_on_vacation():
    data = {"on_vacation": False}
    coordinator = DummyCoordinator(data)
    config_entry = DummyConfigEntry("test", "Test")
    cal = VacancesScolairesCalendar(coordinator, config_entry)
    assert cal.event is None
