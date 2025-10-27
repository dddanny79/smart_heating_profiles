"""Climate platform for Smart Heating Profiles."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_TARGET_ENTITY,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    ATTR_PROFILE,
)
from .profile_manager import HeatingProfileManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smart Heating Profiles climate platform."""
    profile_manager: HeatingProfileManager = hass.data[DOMAIN][entry.entry_id][
        "profile_manager"
    ]
    target_entity = entry.data[CONF_TARGET_ENTITY]
    name = entry.data[CONF_NAME]

    async_add_entities([SmartHeatingProfileClimate(hass, entry, profile_manager, target_entity, name)])


class SmartHeatingProfileClimate(ClimateEntity):
    """Representation of a Smart Heating Profile Climate entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    )

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        profile_manager: HeatingProfileManager,
        target_entity: str,
        name: str,
    ) -> None:
        """Initialize the climate entity."""
        self.hass = hass
        self._entry = entry
        self._profile_manager = profile_manager
        self._target_entity = target_entity
        self._attr_unique_id = f"{entry.entry_id}_climate"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": name,
            "manufacturer": "Smart Heating Profiles",
            "model": "Profile Controller",
        }

        self._attr_min_temp = DEFAULT_MIN_TEMP
        self._attr_max_temp = DEFAULT_MAX_TEMP
        self._attr_target_temperature = None
        self._attr_current_temperature = None
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
        self._attr_preset_modes = list(profile_manager.get_profiles().keys())
        self._attr_preset_mode = profile_manager.get_active_profile()

    async def async_added_to_hass(self) -> None:
        """Run when entity is added to hass."""
        # Track the target climate entity for current temperature
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, self._target_entity, self._async_target_changed
            )
        )

        # Initialize with active profile temperature
        active_temp = self._profile_manager.get_active_temperature()
        if active_temp is not None:
            self._attr_target_temperature = active_temp

        # Get current temperature from target entity
        await self._async_update_from_target()

    @callback
    def _async_target_changed(self, event: Any) -> None:
        """Handle target entity state changes."""
        self.hass.async_create_task(self._async_update_from_target())

    async def _async_update_from_target(self) -> None:
        """Update current temperature from target entity."""
        target_state = self.hass.states.get(self._target_entity)
        if target_state:
            try:
                self._attr_current_temperature = float(
                    target_state.attributes.get("current_temperature", 0)
                )
            except (ValueError, TypeError):
                _LOGGER.warning(
                    "Could not parse current temperature from %s", self._target_entity
                )
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return

        self._attr_target_temperature = temperature

        # Update the target climate entity
        await self.hass.services.async_call(
            "climate",
            "set_temperature",
            {
                "entity_id": self._target_entity,
                "temperature": temperature,
            },
            blocking=True,
        )

        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        self._attr_hvac_mode = hvac_mode

        # Forward to target entity
        target_mode = HVACMode.HEAT if hvac_mode == HVACMode.HEAT else HVACMode.OFF
        await self.hass.services.async_call(
            "climate",
            "set_hvac_mode",
            {
                "entity_id": self._target_entity,
                "hvac_mode": target_mode,
            },
            blocking=True,
        )

        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode (profile)."""
        if await self._profile_manager.async_set_active_profile(preset_mode):
            self._attr_preset_mode = preset_mode

            # Get temperature from the profile and set it
            temperature = self._profile_manager.get_active_temperature()
            if temperature is not None:
                await self.async_set_temperature(temperature=temperature)

            self.async_write_ha_state()
        else:
            _LOGGER.error("Failed to set profile %s", preset_mode)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_PROFILE: self._attr_preset_mode,
            "profiles": self._profile_manager.get_profiles(),
            "target_entity": self._target_entity,
        }
