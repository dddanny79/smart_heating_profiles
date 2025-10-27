"""The Smart Heating Profiles integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_TARGET_ENTITY,
    SERVICE_SET_PROFILE,
    SERVICE_CREATE_PROFILE,
    SERVICE_UPDATE_PROFILE,
    SERVICE_DELETE_PROFILE,
    SERVICE_SET_SCHEDULE,
    SERVICE_ENABLE_SCHEDULE,
    SERVICE_DISABLE_SCHEDULE,
    ATTR_PROFILE,
    ATTR_SCHEDULE_NAME,
    ATTR_SCHEDULE_DAYS,
    ATTR_SCHEDULE_ENABLED,
    ATTR_TIME_BLOCKS,
    ATTR_CONDITIONS,
)
from .profile_manager import HeatingProfileManager
from .schedule_manager import ScheduleManager
from .scheduler import HeatingScheduler

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SWITCH, Platform.SENSOR]

# Service schemas
SERVICE_SET_PROFILE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_PROFILE): cv.string,
    }
)

SERVICE_CREATE_PROFILE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required("profile_name"): cv.string,
        vol.Required(ATTR_TEMPERATURE): vol.Coerce(float),
        vol.Optional("profile_data", default={}): dict,
    }
)

SERVICE_UPDATE_PROFILE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required("profile_name"): cv.string,
        vol.Optional(ATTR_TEMPERATURE): vol.Coerce(float),
        vol.Optional("profile_data", default={}): dict,
    }
)

SERVICE_DELETE_PROFILE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required("profile_name"): cv.string,
    }
)

SERVICE_ENABLE_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_SCHEDULE_NAME): cv.string,
    }
)

SERVICE_DISABLE_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_SCHEDULE_NAME): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Heating Profiles from a config entry."""
    _LOGGER.debug("Setting up Smart Heating Profiles")

    hass.data.setdefault(DOMAIN, {})

    # Create and load profile manager
    profile_manager = HeatingProfileManager(hass, entry.entry_id)
    await profile_manager.async_load()

    # Create and load schedule manager
    schedule_manager = ScheduleManager(hass, entry.entry_id)
    await schedule_manager.async_load()

    # Callback for scheduler to set temperature
    async def set_scheduled_temperature(temperature: float) -> None:
        """Set temperature from scheduler."""
        target_entity = entry.data[CONF_TARGET_ENTITY]
        await hass.services.async_call(
            "climate",
            "set_temperature",
            {
                "entity_id": target_entity,
                "temperature": temperature,
            },
            blocking=True,
        )

    # Create and start scheduler
    scheduler = HeatingScheduler(hass, schedule_manager, set_scheduled_temperature)
    await scheduler.async_start()

    hass.data[DOMAIN][entry.entry_id] = {
        "profile_manager": profile_manager,
        "schedule_manager": schedule_manager,
        "scheduler": scheduler,
    }

    # Register services
    async def handle_set_profile(call: ServiceCall) -> None:
        """Handle set profile service."""
        entity_id = call.data[ATTR_ENTITY_ID]
        profile_name = call.data[ATTR_PROFILE]

        # Find the entry for this entity
        for entry_id, data in hass.data[DOMAIN].items():
            manager: HeatingProfileManager = data.get("profile_manager")
            if manager:
                await manager.async_set_active_profile(profile_name)
                # Trigger state update for the climate entity
                hass.states.async_update(entity_id, None)

    async def handle_create_profile(call: ServiceCall) -> None:
        """Handle create profile service."""
        profile_name = call.data["profile_name"]
        temperature = call.data[ATTR_TEMPERATURE]
        profile_data = call.data.get("profile_data", {})
        profile_data[ATTR_TEMPERATURE] = temperature

        for entry_id, data in hass.data[DOMAIN].items():
            manager: HeatingProfileManager = data.get("profile_manager")
            if manager:
                await manager.async_create_profile(profile_name, profile_data)

    async def handle_update_profile(call: ServiceCall) -> None:
        """Handle update profile service."""
        profile_name = call.data["profile_name"]
        profile_data = call.data.get("profile_data", {})

        if ATTR_TEMPERATURE in call.data:
            profile_data[ATTR_TEMPERATURE] = call.data[ATTR_TEMPERATURE]

        for entry_id, data in hass.data[DOMAIN].items():
            manager: HeatingProfileManager = data.get("profile_manager")
            if manager:
                await manager.async_update_profile(profile_name, profile_data)

    async def handle_delete_profile(call: ServiceCall) -> None:
        """Handle delete profile service."""
        profile_name = call.data["profile_name"]

        for entry_id, data in hass.data[DOMAIN].items():
            manager: HeatingProfileManager = data.get("profile_manager")
            if manager:
                await manager.async_delete_profile(profile_name)

    async def handle_enable_schedule(call: ServiceCall) -> None:
        """Handle enable schedule service."""
        schedule_name = call.data[ATTR_SCHEDULE_NAME]

        for entry_id, data in hass.data[DOMAIN].items():
            manager: ScheduleManager = data.get("schedule_manager")
            if manager:
                await manager.async_enable_schedule(schedule_name)

    async def handle_disable_schedule(call: ServiceCall) -> None:
        """Handle disable schedule service."""
        schedule_name = call.data[ATTR_SCHEDULE_NAME]

        for entry_id, data in hass.data[DOMAIN].items():
            manager: ScheduleManager = data.get("schedule_manager")
            if manager:
                await manager.async_disable_schedule(schedule_name)

    hass.services.async_register(
        DOMAIN, SERVICE_SET_PROFILE, handle_set_profile, schema=SERVICE_SET_PROFILE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_CREATE_PROFILE,
        handle_create_profile,
        schema=SERVICE_CREATE_PROFILE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_UPDATE_PROFILE,
        handle_update_profile,
        schema=SERVICE_UPDATE_PROFILE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_PROFILE,
        handle_delete_profile,
        schema=SERVICE_DELETE_PROFILE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_ENABLE_SCHEDULE,
        handle_enable_schedule,
        schema=SERVICE_ENABLE_SCHEDULE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DISABLE_SCHEDULE,
        handle_disable_schedule,
        schema=SERVICE_DISABLE_SCHEDULE_SCHEMA,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Smart Heating Profiles")

    # Stop scheduler
    scheduler: HeatingScheduler = hass.data[DOMAIN][entry.entry_id].get("scheduler")
    if scheduler:
        await scheduler.async_stop()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)