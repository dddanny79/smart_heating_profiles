"""Sensor platform for Smart Heating Profiles."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_NAME, ALL_WEEKDAYS
from .schedule_manager import ScheduleManager
from .scheduler import HeatingScheduler

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smart Heating Profiles sensor platform."""
    schedule_manager: ScheduleManager = hass.data[DOMAIN][entry.entry_id][
        "schedule_manager"
    ]
    scheduler: HeatingScheduler = hass.data[DOMAIN][entry.entry_id]["scheduler"]
    name = entry.data[CONF_NAME]

    sensors = [
        ScheduleStatusSensor(hass, entry, schedule_manager, scheduler, name),
        NextBlockSensor(hass, entry, schedule_manager, name),
    ]

    async_add_entities(sensors)


class ScheduleStatusSensor(SensorEntity):
    """Sensor showing the current schedule status."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        schedule_manager: ScheduleManager,
        scheduler: HeatingScheduler,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry = entry
        self._schedule_manager = schedule_manager
        self._scheduler = scheduler
        self._attr_unique_id = f"{entry.entry_id}_schedule_status"
        self._attr_name = "Schedule Status"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": name,
            "manufacturer": "Smart Heating Profiles",
            "model": "Profile Controller",
        }

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self._scheduler.is_override_active():
            return "Override Active"

        settings = self._schedule_manager.get_settings()
        if not settings.get("scheduler_enabled", True):
            return "Disabled"

        temperature = self._schedule_manager.get_current_temperature()
        if temperature is not None:
            return "Active"

        return "No Active Schedule"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        now = dt_util.now()
        current_weekday = ALL_WEEKDAYS[now.weekday()]

        temperature = self._schedule_manager.get_current_temperature(now)
        override_info = self._scheduler.get_override_info()

        attrs = {
            "current_day": current_weekday,
            "scheduled_temperature": temperature,
            "override_active": override_info.get("active", False),
        }

        if override_info.get("active"):
            attrs["override_mode"] = override_info.get("mode")
            if "remaining_minutes" in override_info:
                attrs["override_remaining_minutes"] = override_info["remaining_minutes"]
            if "next_block_time" in override_info:
                attrs["override_until"] = override_info["next_block_time"]

        return attrs

    @property
    def icon(self) -> str:
        """Return the icon."""
        if self._scheduler.is_override_active():
            return "mdi:clock-alert"
        if self.native_value == "Active":
            return "mdi:clock-check"
        if self.native_value == "Disabled":
            return "mdi:clock-off"
        return "mdi:clock-outline"


class NextBlockSensor(SensorEntity):
    """Sensor showing information about the next scheduled block."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        schedule_manager: ScheduleManager,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self._entry = entry
        self._schedule_manager = schedule_manager
        self._attr_unique_id = f"{entry.entry_id}_next_block"
        self._attr_name = "Next Schedule"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": name,
            "manufacturer": "Smart Heating Profiles",
            "model": "Profile Controller",
        }

    @property
    def native_value(self) -> float | None:
        """Return the temperature of the next scheduled block."""
        next_time = self._schedule_manager.get_next_block_time()
        if not next_time:
            return None

        # Find the temperature for the next block
        schedules = self._schedule_manager.get_schedules()
        target_time = next_time.strftime("%H:%M")

        for schedule in schedules:
            if not schedule.get("enabled", False):
                continue

            time_blocks = schedule.get("time_blocks", [])
            for block in time_blocks:
                if block.get("time") == target_time:
                    return block.get("temperature")

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        next_time = self._schedule_manager.get_next_block_time()

        if not next_time:
            return {"next_block_time": None}

        now = dt_util.now()
        time_until = next_time - now

        return {
            "next_block_time": next_time.strftime("%H:%M"),
            "next_block_datetime": next_time.isoformat(),
            "minutes_until": int(time_until.total_seconds() / 60),
        }

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:clock-fast"
