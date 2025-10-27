"""Schedule Manager for Smart Heating Profiles."""
from __future__ import annotations

from datetime import datetime, time
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_SCHEDULES,
    CONF_SCHEDULER_ENABLED,
    CONF_OVERRIDE_MODE,
    CONF_OVERRIDE_DURATION,
    ATTR_SCHEDULE_NAME,
    ATTR_SCHEDULE_ENABLED,
    ATTR_SCHEDULE_DAYS,
    ATTR_TIME_BLOCKS,
    ATTR_CONDITIONS,
    ATTR_TIME,
    ATTR_TEMPERATURE,
    DEFAULT_SCHEDULER_ENABLED,
    DEFAULT_OVERRIDE_MODE,
    DEFAULT_OVERRIDE_DURATION,
    ALL_WEEKDAYS,
)

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}_schedules"


class ScheduleManager:
    """Manage heating schedules."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        """Initialize the schedule manager."""
        self.hass = hass
        self.entry_id = entry_id
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry_id}")
        self._schedules: list[dict[str, Any]] = []
        self._settings: dict[str, Any] = {
            CONF_SCHEDULER_ENABLED: DEFAULT_SCHEDULER_ENABLED,
            CONF_OVERRIDE_MODE: DEFAULT_OVERRIDE_MODE,
            CONF_OVERRIDE_DURATION: DEFAULT_OVERRIDE_DURATION,
        }

    async def async_load(self) -> None:
        """Load schedules from storage."""
        data = await self._store.async_load()

        if data is None:
            # Initialize with default schedule
            self._schedules = [
                {
                    ATTR_SCHEDULE_NAME: "Weekday Schedule",
                    ATTR_SCHEDULE_ENABLED: True,
                    ATTR_SCHEDULE_DAYS: ALL_WEEKDAYS[:5],  # Mon-Fri
                    ATTR_TIME_BLOCKS: [
                        {ATTR_TIME: "06:00", ATTR_TEMPERATURE: 22.0},
                        {ATTR_TIME: "09:00", ATTR_TEMPERATURE: 18.0},
                        {ATTR_TIME: "17:00", ATTR_TEMPERATURE: 21.0},
                        {ATTR_TIME: "22:00", ATTR_TEMPERATURE: 17.0},
                    ],
                    ATTR_CONDITIONS: [],
                }
            ]
            await self.async_save()
        else:
            self._schedules = data.get(CONF_SCHEDULES, [])
            self._settings = data.get("settings", self._settings)

        _LOGGER.debug("Loaded %d schedules", len(self._schedules))

    async def async_save(self) -> None:
        """Save schedules to storage."""
        data = {
            CONF_SCHEDULES: self._schedules,
            "settings": self._settings,
        }
        await self._store.async_save(data)
        _LOGGER.debug("Saved schedules to storage")

    def get_schedules(self) -> list[dict[str, Any]]:
        """Get all schedules."""
        return self._schedules.copy()

    def get_schedule(self, name: str) -> dict[str, Any] | None:
        """Get a specific schedule by name."""
        for schedule in self._schedules:
            if schedule.get(ATTR_SCHEDULE_NAME) == name:
                return schedule.copy()
        return None

    def get_settings(self) -> dict[str, Any]:
        """Get scheduler settings."""
        return self._settings.copy()

    async def async_add_schedule(self, schedule_data: dict[str, Any]) -> bool:
        """Add a new schedule."""
        name = schedule_data.get(ATTR_SCHEDULE_NAME)
        if not name:
            _LOGGER.error("Schedule must have a name")
            return False

        # Check if name already exists
        if self.get_schedule(name) is not None:
            _LOGGER.error("Schedule with name %s already exists", name)
            return False

        # Validate schedule data
        if not self._validate_schedule(schedule_data):
            return False

        self._schedules.append(schedule_data)
        await self.async_save()
        _LOGGER.info("Added schedule %s", name)
        return True

    async def async_update_schedule(
        self, name: str, schedule_data: dict[str, Any]
    ) -> bool:
        """Update an existing schedule."""
        for i, schedule in enumerate(self._schedules):
            if schedule.get(ATTR_SCHEDULE_NAME) == name:
                # Validate schedule data
                if not self._validate_schedule(schedule_data):
                    return False

                self._schedules[i] = schedule_data
                await self.async_save()
                _LOGGER.info("Updated schedule %s", name)
                return True

        _LOGGER.error("Schedule %s not found", name)
        return False

    async def async_delete_schedule(self, name: str) -> bool:
        """Delete a schedule."""
        for i, schedule in enumerate(self._schedules):
            if schedule.get(ATTR_SCHEDULE_NAME) == name:
                del self._schedules[i]
                await self.async_save()
                _LOGGER.info("Deleted schedule %s", name)
                return True

        _LOGGER.error("Schedule %s not found", name)
        return False

    async def async_enable_schedule(self, name: str) -> bool:
        """Enable a schedule."""
        for schedule in self._schedules:
            if schedule.get(ATTR_SCHEDULE_NAME) == name:
                schedule[ATTR_SCHEDULE_ENABLED] = True
                await self.async_save()
                _LOGGER.info("Enabled schedule %s", name)
                return True

        _LOGGER.error("Schedule %s not found", name)
        return False

    async def async_disable_schedule(self, name: str) -> bool:
        """Disable a schedule."""
        for schedule in self._schedules:
            if schedule.get(ATTR_SCHEDULE_NAME) == name:
                schedule[ATTR_SCHEDULE_ENABLED] = False
                await self.async_save()
                _LOGGER.info("Disabled schedule %s", name)
                return True

        _LOGGER.error("Schedule %s not found", name)
        return False

    async def async_update_settings(self, settings: dict[str, Any]) -> bool:
        """Update scheduler settings."""
        self._settings.update(settings)
        await self.async_save()
        _LOGGER.info("Updated scheduler settings")
        return True

    def get_current_temperature(self, now: datetime | None = None) -> float | None:
        """Get the temperature for the current time based on active schedules."""
        if not self._settings.get(CONF_SCHEDULER_ENABLED, True):
            return None

        if now is None:
            now = dt_util.now()

        current_weekday = ALL_WEEKDAYS[now.weekday()]
        current_time = now.time()

        # Find all matching schedules for current day
        matching_schedules = []
        for schedule in self._schedules:
            if not schedule.get(ATTR_SCHEDULE_ENABLED, False):
                continue

            if current_weekday not in schedule.get(ATTR_SCHEDULE_DAYS, []):
                continue

            # Check conditions
            if not self._check_conditions(schedule.get(ATTR_CONDITIONS, [])):
                continue

            matching_schedules.append(schedule)

        if not matching_schedules:
            return None

        # Find the active time block from all matching schedules
        # Priority: Last scheduled time that has passed
        active_temperature = None
        latest_time = None

        for schedule in matching_schedules:
            time_blocks = schedule.get(ATTR_TIME_BLOCKS, [])
            sorted_blocks = sorted(time_blocks, key=lambda x: x[ATTR_TIME])

            for block in sorted_blocks:
                block_time = time.fromisoformat(block[ATTR_TIME])
                if block_time <= current_time:
                    if latest_time is None or block_time > latest_time:
                        latest_time = block_time
                        active_temperature = block[ATTR_TEMPERATURE]

        return active_temperature

    def get_next_block_time(self, now: datetime | None = None) -> datetime | None:
        """Get the next scheduled time block."""
        if now is None:
            now = dt_util.now()

        current_weekday = ALL_WEEKDAYS[now.weekday()]
        current_time = now.time()

        next_block = None
        next_time = None

        # Check today's schedules
        for schedule in self._schedules:
            if not schedule.get(ATTR_SCHEDULE_ENABLED, False):
                continue

            if current_weekday not in schedule.get(ATTR_SCHEDULE_DAYS, []):
                continue

            if not self._check_conditions(schedule.get(ATTR_CONDITIONS, [])):
                continue

            time_blocks = schedule.get(ATTR_TIME_BLOCKS, [])
            for block in time_blocks:
                block_time = time.fromisoformat(block[ATTR_TIME])
                if block_time > current_time:
                    block_datetime = now.replace(
                        hour=block_time.hour,
                        minute=block_time.minute,
                        second=0,
                        microsecond=0,
                    )
                    if next_time is None or block_datetime < next_time:
                        next_time = block_datetime

        # TODO: Check next days if no block found today

        return next_time

    def _validate_schedule(self, schedule_data: dict[str, Any]) -> bool:
        """Validate schedule data."""
        # Check required fields
        if ATTR_SCHEDULE_NAME not in schedule_data:
            _LOGGER.error("Schedule must have a name")
            return False

        if ATTR_SCHEDULE_DAYS not in schedule_data:
            _LOGGER.error("Schedule must have days")
            return False

        if ATTR_TIME_BLOCKS not in schedule_data:
            _LOGGER.error("Schedule must have time blocks")
            return False

        # Validate days
        days = schedule_data[ATTR_SCHEDULE_DAYS]
        if not days or not all(day in ALL_WEEKDAYS for day in days):
            _LOGGER.error("Invalid days in schedule")
            return False

        # Validate time blocks
        time_blocks = schedule_data[ATTR_TIME_BLOCKS]
        if not time_blocks:
            _LOGGER.error("Schedule must have at least one time block")
            return False

        for block in time_blocks:
            if ATTR_TIME not in block or ATTR_TEMPERATURE not in block:
                _LOGGER.error("Time block must have time and temperature")
                return False

            # Validate time format
            try:
                time.fromisoformat(block[ATTR_TIME])
            except ValueError:
                _LOGGER.error("Invalid time format in block: %s", block[ATTR_TIME])
                return False

            # Validate temperature
            try:
                float(block[ATTR_TEMPERATURE])
            except ValueError:
                _LOGGER.error(
                    "Invalid temperature in block: %s", block[ATTR_TEMPERATURE]
                )
                return False

        return True

    def _check_conditions(self, conditions: list[dict[str, Any]]) -> bool:
        """Check if all conditions are met."""
        if not conditions:
            return True

        for condition in conditions:
            entity_id = condition.get("entity_id")
            required_state = condition.get("state")

            if not entity_id or required_state is None:
                continue

            state = self.hass.states.get(entity_id)
            if state is None or state.state != required_state:
                return False

        return True
