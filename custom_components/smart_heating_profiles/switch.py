"""Switch platform for Smart Heating Profiles."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_NAME, CONF_SCHEDULER_ENABLED
from .schedule_manager import ScheduleManager
from .scheduler import HeatingScheduler

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smart Heating Profiles switch platform."""
    schedule_manager: ScheduleManager = hass.data[DOMAIN][entry.entry_id][
        "schedule_manager"
    ]
    scheduler: HeatingScheduler = hass.data[DOMAIN][entry.entry_id]["scheduler"]
    name = entry.data[CONF_NAME]

    switches = [
        SchedulerMasterSwitch(hass, entry, schedule_manager, scheduler, name),
    ]

    async_add_entities(switches)


class SchedulerMasterSwitch(SwitchEntity):
    """Switch to enable/disable the heating scheduler."""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        schedule_manager: ScheduleManager,
        scheduler: HeatingScheduler,
        name: str,
    ) -> None:
        """Initialize the switch."""
        self.hass = hass
        self._entry = entry
        self._schedule_manager = schedule_manager
        self._scheduler = scheduler
        self._attr_unique_id = f"{entry.entry_id}_scheduler_switch"
        self._attr_name = "Scheduler"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": name,
            "manufacturer": "Smart Heating Profiles",
            "model": "Profile Controller",
        }

        # Load initial state
        settings = schedule_manager.get_settings()
        self._attr_is_on = settings.get(CONF_SCHEDULER_ENABLED, True)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the scheduler."""
        await self._schedule_manager.async_update_settings(
            {CONF_SCHEDULER_ENABLED: True}
        )
        self._attr_is_on = True
        self.async_write_ha_state()
        _LOGGER.info("Scheduler enabled")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the scheduler."""
        await self._schedule_manager.async_update_settings(
            {CONF_SCHEDULER_ENABLED: False}
        )
        self._attr_is_on = False
        self.async_write_ha_state()
        _LOGGER.info("Scheduler disabled")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        settings = self._schedule_manager.get_settings()
        schedules = self._schedule_manager.get_schedules()
        override_info = self._scheduler.get_override_info()

        enabled_schedules = [
            s["schedule_name"] for s in schedules if s.get("enabled", False)
        ]

        return {
            "override_mode": settings.get("override_mode"),
            "override_duration": settings.get("override_duration"),
            "override_active": override_info.get("active", False),
            "total_schedules": len(schedules),
            "enabled_schedules": enabled_schedules,
            "schedules_count": len(enabled_schedules),
        }

    @property
    def icon(self) -> str:
        """Return the icon."""
        if self._attr_is_on:
            return "mdi:clock-check"
        return "mdi:clock-off"
