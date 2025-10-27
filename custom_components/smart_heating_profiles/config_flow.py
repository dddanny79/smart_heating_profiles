"""Config flow for Smart Heating Profiles integration."""
from __future__ import annotations

import logging
from typing import Any
import copy

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_TARGET_ENTITY,
    CONF_OVERRIDE_MODE,
    CONF_OVERRIDE_DURATION,
    DEFAULT_NAME,
    DEFAULT_OVERRIDE_MODE,
    DEFAULT_OVERRIDE_DURATION,
    OVERRIDE_MODE_TIMER,
    OVERRIDE_MODE_NEXT_BLOCK,
    ATTR_SCHEDULE_NAME,
    ATTR_SCHEDULE_ENABLED,
    ATTR_SCHEDULE_DAYS,
    ATTR_TIME_BLOCKS,
    ATTR_CONDITIONS,
    ATTR_TIME,
    ATTR_TEMPERATURE,
    ALL_WEEKDAYS,
)
from .schedule_manager import ScheduleManager

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Validate that the target entity exists
    target_entity = data[CONF_TARGET_ENTITY]
    state = hass.states.get(target_entity)

    if state is None:
        raise ValueError(f"Entity {target_entity} not found")

    if not target_entity.startswith("climate."):
        raise ValueError("Target entity must be a climate entity")

    return {"title": data[CONF_NAME]}


class SmartHeatingProfilesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Heating Profiles."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except ValueError as err:
                _LOGGER.error("Validation error: %s", err)
                errors["base"] = "invalid_entity"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID based on target entity
                await self.async_set_unique_id(user_input[CONF_TARGET_ENTITY])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Required(CONF_TARGET_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="climate"),
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SmartHeatingProfilesOptionsFlowHandler:
        """Get the options flow for this handler."""
        return SmartHeatingProfilesOptionsFlowHandler(config_entry)


class SmartHeatingProfilesOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Smart Heating Profiles."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._schedule_manager: ScheduleManager | None = None
        self._current_schedule: dict[str, Any] | None = None
        self._edit_schedule_name: str | None = None

    def _get_schedule_manager(self) -> ScheduleManager:
        """Get the schedule manager."""
        if self._schedule_manager is None:
            self._schedule_manager = self.hass.data[DOMAIN][self.config_entry.entry_id][
                "schedule_manager"
            ]
        return self._schedule_manager

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - Main menu."""
        if user_input is not None:
            if user_input.get("action") == "schedules":
                return await self.async_step_schedule_list()
            if user_input.get("action") == "settings":
                return await self.async_step_settings()

        return self.async_show_menu(
            step_id="init",
            menu_options=["schedules", "settings"],
        )

    async def async_step_schedules(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Redirect to schedule list."""
        return await self.async_step_schedule_list()

    async def async_step_schedule_list(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show list of schedules."""
        manager = self._get_schedule_manager()
        schedules = manager.get_schedules()

        if user_input is not None:
            action = user_input.get("action")
            if action == "create":
                return await self.async_step_schedule_create()
            elif action and action.startswith("edit_"):
                schedule_name = action[5:]  # Remove "edit_" prefix
                self._edit_schedule_name = schedule_name
                self._current_schedule = manager.get_schedule(schedule_name)
                if self._current_schedule:
                    return await self.async_step_schedule_edit()
            elif action and action.startswith("delete_"):
                schedule_name = action[7:]  # Remove "delete_" prefix
                await manager.async_delete_schedule(schedule_name)
                return await self.async_step_schedule_list()

        # Build schema with schedule list
        schedule_options = {"create": "Create New Schedule"}
        for schedule in schedules:
            name = schedule.get(ATTR_SCHEDULE_NAME, "Unknown")
            enabled = "✓" if schedule.get(ATTR_SCHEDULE_ENABLED, False) else "✗"
            days_count = len(schedule.get(ATTR_SCHEDULE_DAYS, []))
            blocks_count = len(schedule.get(ATTR_TIME_BLOCKS, []))
            schedule_options[f"edit_{name}"] = f"{enabled} {name} ({days_count} days, {blocks_count} blocks)"

        for schedule in schedules:
            name = schedule.get(ATTR_SCHEDULE_NAME, "Unknown")
            schedule_options[f"delete_{name}"] = f"🗑️ Delete: {name}"

        data_schema = vol.Schema(
            {
                vol.Required("action"): vol.In(schedule_options),
            }
        )

        return self.async_show_form(
            step_id="schedule_list",
            data_schema=data_schema,
            description_placeholders={"schedules_count": str(len(schedules))},
        )

    async def async_step_schedule_create(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Create a new schedule."""
        errors = {}

        if user_input is not None:
            schedule_name = user_input.get(ATTR_SCHEDULE_NAME, "").strip()

            if not schedule_name:
                errors["base"] = "name_required"
            else:
                # Create initial schedule with one time block
                new_schedule = {
                    ATTR_SCHEDULE_NAME: schedule_name,
                    ATTR_SCHEDULE_ENABLED: user_input.get(ATTR_SCHEDULE_ENABLED, True),
                    ATTR_SCHEDULE_DAYS: user_input.get(ATTR_SCHEDULE_DAYS, ALL_WEEKDAYS),
                    ATTR_TIME_BLOCKS: [
                        {ATTR_TIME: "07:00", ATTR_TEMPERATURE: 21.0}
                    ],
                    ATTR_CONDITIONS: [],
                }

                manager = self._get_schedule_manager()
                if await manager.async_add_schedule(new_schedule):
                    self._edit_schedule_name = schedule_name
                    self._current_schedule = new_schedule
                    return await self.async_step_schedule_edit()
                else:
                    errors["base"] = "schedule_exists"

        data_schema = vol.Schema(
            {
                vol.Required(ATTR_SCHEDULE_NAME): cv.string,
                vol.Required(ATTR_SCHEDULE_ENABLED, default=True): cv.boolean,
                vol.Required(ATTR_SCHEDULE_DAYS, default=ALL_WEEKDAYS): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=ALL_WEEKDAYS,
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="schedule_create",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_schedule_edit(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit a schedule."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "edit_blocks":
                return await self.async_step_time_blocks()
            elif action == "edit_conditions":
                return await self.async_step_conditions()
            elif action == "toggle_enabled":
                manager = self._get_schedule_manager()
                schedule = manager.get_schedule(self._edit_schedule_name)
                if schedule:
                    schedule[ATTR_SCHEDULE_ENABLED] = not schedule.get(ATTR_SCHEDULE_ENABLED, False)
                    await manager.async_update_schedule(self._edit_schedule_name, schedule)
                    self._current_schedule = schedule
                return await self.async_step_schedule_edit()
            elif action == "edit_days":
                return await self.async_step_edit_days()
            elif action == "done":
                return await self.async_step_schedule_list()

        schedule = self._current_schedule
        if not schedule:
            return await self.async_step_schedule_list()

        enabled_text = "Enabled ✓" if schedule.get(ATTR_SCHEDULE_ENABLED, False) else "Disabled ✗"
        days = schedule.get(ATTR_SCHEDULE_DAYS, [])
        days_text = ", ".join([d[:3].upper() for d in days])
        blocks = schedule.get(ATTR_TIME_BLOCKS, [])
        blocks_text = "\n".join([f"  {b.get(ATTR_TIME)} → {b.get(ATTR_TEMPERATURE)}°C" for b in blocks])
        conditions = schedule.get(ATTR_CONDITIONS, [])
        conditions_count = len(conditions)

        data_schema = vol.Schema(
            {
                vol.Required("action"): vol.In({
                    "edit_blocks": f"Edit Time Blocks ({len(blocks)})",
                    "edit_days": f"Edit Days ({days_text})",
                    "edit_conditions": f"Edit Conditions ({conditions_count})",
                    "toggle_enabled": f"Status: {enabled_text}",
                    "done": "Done",
                }),
            }
        )

        return self.async_show_form(
            step_id="schedule_edit",
            data_schema=data_schema,
            description_placeholders={
                "schedule_name": schedule.get(ATTR_SCHEDULE_NAME, ""),
                "blocks": blocks_text,
            },
        )

    async def async_step_edit_days(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit schedule days."""
        if user_input is not None:
            manager = self._get_schedule_manager()
            schedule = manager.get_schedule(self._edit_schedule_name)
            if schedule:
                schedule[ATTR_SCHEDULE_DAYS] = user_input.get(ATTR_SCHEDULE_DAYS, ALL_WEEKDAYS)
                await manager.async_update_schedule(self._edit_schedule_name, schedule)
                self._current_schedule = schedule
            return await self.async_step_schedule_edit()

        schedule = self._current_schedule
        current_days = schedule.get(ATTR_SCHEDULE_DAYS, ALL_WEEKDAYS) if schedule else ALL_WEEKDAYS

        data_schema = vol.Schema(
            {
                vol.Required(ATTR_SCHEDULE_DAYS, default=current_days): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=ALL_WEEKDAYS,
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_days",
            data_schema=data_schema,
        )

    async def async_step_time_blocks(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage time blocks."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "add":
                return await self.async_step_add_block()
            elif action and action.startswith("delete_"):
                index = int(action[7:])
                manager = self._get_schedule_manager()
                schedule = manager.get_schedule(self._edit_schedule_name)
                if schedule and ATTR_TIME_BLOCKS in schedule:
                    blocks = schedule[ATTR_TIME_BLOCKS]
                    if 0 <= index < len(blocks):
                        blocks.pop(index)
                        await manager.async_update_schedule(self._edit_schedule_name, schedule)
                        self._current_schedule = schedule
                return await self.async_step_time_blocks()
            elif action == "done":
                return await self.async_step_schedule_edit()

        schedule = self._current_schedule
        if not schedule:
            return await self.async_step_schedule_edit()

        blocks = schedule.get(ATTR_TIME_BLOCKS, [])

        block_options = {"add": "➕ Add Time Block"}
        for i, block in enumerate(blocks):
            time_str = block.get(ATTR_TIME, "??:??")
            temp = block.get(ATTR_TEMPERATURE, 0)
            block_options[f"delete_{i}"] = f"🗑️ {time_str} → {temp}°C"

        block_options["done"] = "Done"

        data_schema = vol.Schema(
            {
                vol.Required("action"): vol.In(block_options),
            }
        )

        return self.async_show_form(
            step_id="time_blocks",
            data_schema=data_schema,
        )

    async def async_step_add_block(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a time block."""
        errors = {}

        if user_input is not None:
            time_str = user_input.get(ATTR_TIME, "")
            temperature = user_input.get(ATTR_TEMPERATURE, 20.0)

            # Validate time format
            try:
                parts = time_str.split(":")
                if len(parts) != 2:
                    errors["base"] = "invalid_time"
                else:
                    hour = int(parts[0])
                    minute = int(parts[1])
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        errors["base"] = "invalid_time"
            except (ValueError, AttributeError):
                errors["base"] = "invalid_time"

            if not errors:
                manager = self._get_schedule_manager()
                schedule = manager.get_schedule(self._edit_schedule_name)
                if schedule:
                    blocks = schedule.get(ATTR_TIME_BLOCKS, [])
                    blocks.append({ATTR_TIME: time_str, ATTR_TEMPERATURE: temperature})
                    # Sort blocks by time
                    blocks.sort(key=lambda x: x.get(ATTR_TIME, ""))
                    schedule[ATTR_TIME_BLOCKS] = blocks
                    await manager.async_update_schedule(self._edit_schedule_name, schedule)
                    self._current_schedule = schedule
                return await self.async_step_time_blocks()

        data_schema = vol.Schema(
            {
                vol.Required(ATTR_TIME, default="12:00"): cv.string,
                vol.Required(ATTR_TEMPERATURE, default=21.0): vol.All(
                    vol.Coerce(float), vol.Range(min=5.0, max=30.0)
                ),
            }
        )

        return self.async_show_form(
            step_id="add_block",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_conditions(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage conditions."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "add":
                return await self.async_step_add_condition()
            elif action and action.startswith("delete_"):
                index = int(action[7:])
                manager = self._get_schedule_manager()
                schedule = manager.get_schedule(self._edit_schedule_name)
                if schedule and ATTR_CONDITIONS in schedule:
                    conditions = schedule[ATTR_CONDITIONS]
                    if 0 <= index < len(conditions):
                        conditions.pop(index)
                        await manager.async_update_schedule(self._edit_schedule_name, schedule)
                        self._current_schedule = schedule
                return await self.async_step_conditions()
            elif action == "done":
                return await self.async_step_schedule_edit()

        schedule = self._current_schedule
        if not schedule:
            return await self.async_step_schedule_edit()

        conditions = schedule.get(ATTR_CONDITIONS, [])

        condition_options = {"add": "➕ Add Condition"}
        for i, condition in enumerate(conditions):
            entity = condition.get("entity_id", "unknown")
            state = condition.get("state", "unknown")
            condition_options[f"delete_{i}"] = f"🗑️ {entity} = {state}"

        condition_options["done"] = "Done"

        data_schema = vol.Schema(
            {
                vol.Required("action"): vol.In(condition_options),
            }
        )

        return self.async_show_form(
            step_id="conditions",
            data_schema=data_schema,
        )

    async def async_step_add_condition(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a condition."""
        if user_input is not None:
            entity_id = user_input.get("entity_id", "")
            state = user_input.get("state", "on")

            manager = self._get_schedule_manager()
            schedule = manager.get_schedule(self._edit_schedule_name)
            if schedule:
                conditions = schedule.get(ATTR_CONDITIONS, [])
                conditions.append({"entity_id": entity_id, "state": state})
                schedule[ATTR_CONDITIONS] = conditions
                await manager.async_update_schedule(self._edit_schedule_name, schedule)
                self._current_schedule = schedule
            return await self.async_step_conditions()

        data_schema = vol.Schema(
            {
                vol.Required("entity_id"): selector.EntitySelector(
                    selector.EntitySelectorConfig()
                ),
                vol.Required("state", default="on"): cv.string,
            }
        )

        return self.async_show_form(
            step_id="add_condition",
            data_schema=data_schema,
        )

    async def async_step_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure scheduler settings."""
        if user_input is not None:
            manager = self._get_schedule_manager()
            settings = {
                CONF_OVERRIDE_MODE: user_input.get(CONF_OVERRIDE_MODE, DEFAULT_OVERRIDE_MODE),
                CONF_OVERRIDE_DURATION: user_input.get(CONF_OVERRIDE_DURATION, DEFAULT_OVERRIDE_DURATION),
            }
            await manager.async_update_settings(settings)
            return self.async_create_entry(title="", data={})

        manager = self._get_schedule_manager()
        current_settings = manager.get_settings()

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_OVERRIDE_MODE,
                    default=current_settings.get(CONF_OVERRIDE_MODE, DEFAULT_OVERRIDE_MODE),
                ): vol.In({
                    OVERRIDE_MODE_TIMER: "Timer (resume after X minutes)",
                    OVERRIDE_MODE_NEXT_BLOCK: "Next Block (resume at next scheduled time)",
                }),
                vol.Required(
                    CONF_OVERRIDE_DURATION,
                    default=current_settings.get(CONF_OVERRIDE_DURATION, DEFAULT_OVERRIDE_DURATION),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
            }
        )

        return self.async_show_form(
            step_id="settings",
            data_schema=data_schema,
        )
