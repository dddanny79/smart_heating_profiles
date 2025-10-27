"""Scheduler for Smart Heating Profiles."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any, Callable

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_point_in_time, async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import (
    CONF_SCHEDULER_ENABLED,
    CONF_OVERRIDE_MODE,
    CONF_OVERRIDE_DURATION,
    OVERRIDE_MODE_TIMER,
    OVERRIDE_MODE_NEXT_BLOCK,
)
from .schedule_manager import ScheduleManager

_LOGGER = logging.getLogger(__name__)

CHECK_INTERVAL = timedelta(minutes=1)


class HeatingScheduler:
    """Handle time-based profile switching with override support."""

    def __init__(
        self,
        hass: HomeAssistant,
        schedule_manager: ScheduleManager,
        temperature_callback: Callable[[float], None],
    ) -> None:
        """Initialize the scheduler."""
        self.hass = hass
        self._schedule_manager = schedule_manager
        self._temperature_callback = temperature_callback
        self._unsub_interval = None
        self._unsub_next_check = None
        self._override_active = False
        self._override_end_time = None
        self._last_temperature = None

    async def async_start(self) -> None:
        """Start the scheduler."""
        _LOGGER.info("Starting heating scheduler")

        # Initial check
        await self._async_check_schedule()

        # Schedule periodic checks every minute
        self._unsub_interval = async_track_time_interval(
            self.hass, self._async_check_schedule, CHECK_INTERVAL
        )

    async def async_stop(self) -> None:
        """Stop the scheduler."""
        _LOGGER.info("Stopping heating scheduler")

        if self._unsub_interval:
            self._unsub_interval()
            self._unsub_interval = None

        if self._unsub_next_check:
            self._unsub_next_check()
            self._unsub_next_check = None

    @callback
    async def _async_check_schedule(self, now: datetime | None = None) -> None:
        """Check and apply scheduled temperature."""
        if now is None:
            now = dt_util.now()

        settings = self._schedule_manager.get_settings()

        # Check if scheduler is enabled
        if not settings.get(CONF_SCHEDULER_ENABLED, True):
            _LOGGER.debug("Scheduler is disabled")
            return

        # Check if override is active
        if self._override_active:
            override_mode = settings.get(CONF_OVERRIDE_MODE, OVERRIDE_MODE_NEXT_BLOCK)

            if override_mode == OVERRIDE_MODE_TIMER:
                # Timer mode: Check if override time has expired
                if self._override_end_time and now >= self._override_end_time:
                    _LOGGER.info("Override timer expired, resuming schedule")
                    self._override_active = False
                    self._override_end_time = None
                else:
                    _LOGGER.debug("Override active (timer mode), skipping schedule")
                    return

            elif override_mode == OVERRIDE_MODE_NEXT_BLOCK:
                # Next block mode: Check if we've reached the next scheduled block
                next_block_time = self._schedule_manager.get_next_block_time(now)
                if next_block_time and now >= next_block_time:
                    _LOGGER.info("Next scheduled block reached, resuming schedule")
                    self._override_active = False
                    self._override_end_time = None
                else:
                    _LOGGER.debug("Override active (next block mode), skipping schedule")
                    return

        # Get scheduled temperature
        temperature = self._schedule_manager.get_current_temperature(now)

        if temperature is None:
            _LOGGER.debug("No active schedule for current time")
            return

        # Only update if temperature changed
        if temperature != self._last_temperature:
            _LOGGER.info("Applying scheduled temperature: %.1f°C", temperature)
            self._last_temperature = temperature
            await self._temperature_callback(temperature)

    async def async_manual_override(self) -> None:
        """Activate manual override mode."""
        settings = self._schedule_manager.get_settings()
        override_mode = settings.get(CONF_OVERRIDE_MODE, OVERRIDE_MODE_NEXT_BLOCK)

        self._override_active = True

        if override_mode == OVERRIDE_MODE_TIMER:
            duration = settings.get(CONF_OVERRIDE_DURATION, 60)
            self._override_end_time = dt_util.now() + timedelta(minutes=duration)
            _LOGGER.info(
                "Manual override activated (timer mode: %d minutes)", duration
            )
        else:
            self._override_end_time = None
            _LOGGER.info("Manual override activated (next block mode)")

    async def async_clear_override(self) -> None:
        """Clear manual override and resume schedule."""
        self._override_active = False
        self._override_end_time = None
        _LOGGER.info("Manual override cleared")

        # Immediately check schedule
        await self._async_check_schedule()

    def is_override_active(self) -> bool:
        """Check if override is currently active."""
        return self._override_active

    def get_override_info(self) -> dict[str, Any]:
        """Get information about current override state."""
        settings = self._schedule_manager.get_settings()

        info = {
            "active": self._override_active,
            "mode": settings.get(CONF_OVERRIDE_MODE, OVERRIDE_MODE_NEXT_BLOCK),
        }

        if self._override_active:
            if self._override_end_time:
                info["end_time"] = self._override_end_time.isoformat()
                remaining = (self._override_end_time - dt_util.now()).total_seconds() / 60
                info["remaining_minutes"] = max(0, int(remaining))
            else:
                next_block = self._schedule_manager.get_next_block_time()
                if next_block:
                    info["next_block_time"] = next_block.isoformat()

        return info
