"""Profile Manager for Smart Heating Profiles."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import (
    DOMAIN,
    DEFAULT_PROFILES,
    ATTR_TEMPERATURE,
    PRESET_COMFORT,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}_profiles"


class HeatingProfileManager:
    """Manage heating profiles."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        """Initialize the profile manager."""
        self.hass = hass
        self.entry_id = entry_id
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry_id}")
        self._profiles: dict[str, dict[str, Any]] = {}
        self._active_profile: str | None = None

    async def async_load(self) -> None:
        """Load profiles from storage."""
        data = await self._store.async_load()

        if data is None:
            # Initialize with default profiles
            self._profiles = DEFAULT_PROFILES.copy()
            self._active_profile = PRESET_COMFORT
            await self.async_save()
        else:
            self._profiles = data.get("profiles", DEFAULT_PROFILES.copy())
            self._active_profile = data.get("active_profile", PRESET_COMFORT)

        _LOGGER.debug(
            "Loaded %d profiles, active: %s", len(self._profiles), self._active_profile
        )

    async def async_save(self) -> None:
        """Save profiles to storage."""
        data = {
            "profiles": self._profiles,
            "active_profile": self._active_profile,
        }
        await self._store.async_save(data)
        _LOGGER.debug("Saved profiles to storage")

    def get_profiles(self) -> dict[str, dict[str, Any]]:
        """Get all profiles."""
        return self._profiles.copy()

    def get_profile(self, profile_name: str) -> dict[str, Any] | None:
        """Get a specific profile."""
        return self._profiles.get(profile_name)

    def get_active_profile(self) -> str | None:
        """Get the active profile name."""
        return self._active_profile

    def get_active_temperature(self) -> float | None:
        """Get the temperature of the active profile."""
        if self._active_profile is None:
            return None

        profile = self._profiles.get(self._active_profile)
        if profile is None:
            return None

        return profile.get(ATTR_TEMPERATURE)

    async def async_set_active_profile(self, profile_name: str) -> bool:
        """Set the active profile."""
        if profile_name not in self._profiles:
            _LOGGER.error("Profile %s does not exist", profile_name)
            return False

        self._active_profile = profile_name
        await self.async_save()
        _LOGGER.info("Set active profile to %s", profile_name)
        return True

    async def async_create_profile(
        self, profile_name: str, profile_data: dict[str, Any]
    ) -> bool:
        """Create a new profile."""
        if profile_name in self._profiles:
            _LOGGER.error("Profile %s already exists", profile_name)
            return False

        if ATTR_TEMPERATURE not in profile_data:
            _LOGGER.error("Profile data must contain temperature")
            return False

        self._profiles[profile_name] = profile_data.copy()
        await self.async_save()
        _LOGGER.info("Created profile %s", profile_name)
        return True

    async def async_update_profile(
        self, profile_name: str, profile_data: dict[str, Any]
    ) -> bool:
        """Update an existing profile."""
        if profile_name not in self._profiles:
            _LOGGER.error("Profile %s does not exist", profile_name)
            return False

        if ATTR_TEMPERATURE not in profile_data:
            _LOGGER.error("Profile data must contain temperature")
            return False

        self._profiles[profile_name].update(profile_data)
        await self.async_save()
        _LOGGER.info("Updated profile %s", profile_name)
        return True

    async def async_delete_profile(self, profile_name: str) -> bool:
        """Delete a profile."""
        if profile_name not in self._profiles:
            _LOGGER.error("Profile %s does not exist", profile_name)
            return False

        # Don't delete if it's the active profile
        if profile_name == self._active_profile:
            _LOGGER.error("Cannot delete active profile %s", profile_name)
            return False

        del self._profiles[profile_name]
        await self.async_save()
        _LOGGER.info("Deleted profile %s", profile_name)
        return True
