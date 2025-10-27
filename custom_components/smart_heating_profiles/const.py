"""Constants for the Smart Heating Profiles integration."""
from typing import Final

DOMAIN: Final = "smart_heating_profiles"

# Configuration
CONF_NAME: Final = "name"
CONF_TARGET_ENTITY: Final = "target_entity"
CONF_PROFILES: Final = "profiles"

# Profile attributes
ATTR_PROFILE: Final = "profile"
ATTR_TEMPERATURE: Final = "temperature"
ATTR_ACTIVE: Final = "active"
ATTR_SCHEDULE: Final = "schedule"

# Default values
DEFAULT_NAME: Final = "Smart Heating Profile"
DEFAULT_TEMPERATURE: Final = 20.0
DEFAULT_MIN_TEMP: Final = 5.0
DEFAULT_MAX_TEMP: Final = 30.0

# Services
SERVICE_SET_PROFILE: Final = "set_profile"
SERVICE_CREATE_PROFILE: Final = "create_profile"
SERVICE_DELETE_PROFILE: Final = "delete_profile"
SERVICE_UPDATE_PROFILE: Final = "update_profile"

# Profile presets
PRESET_COMFORT: Final = "comfort"
PRESET_ECO: Final = "eco"
PRESET_AWAY: Final = "away"
PRESET_SLEEP: Final = "sleep"
PRESET_HOME: Final = "home"

DEFAULT_PROFILES: Final = {
    PRESET_COMFORT: {"temperature": 22.0, "name": "Comfort"},
    PRESET_ECO: {"temperature": 18.0, "name": "Eco"},
    PRESET_AWAY: {"temperature": 15.0, "name": "Away"},
    PRESET_SLEEP: {"temperature": 17.0, "name": "Sleep"},
    PRESET_HOME: {"temperature": 21.0, "name": "Home"},
}

# Scheduler configuration
CONF_SCHEDULES: Final = "schedules"
CONF_SCHEDULER_ENABLED: Final = "scheduler_enabled"
CONF_OVERRIDE_MODE: Final = "override_mode"
CONF_OVERRIDE_DURATION: Final = "override_duration"

# Schedule attributes
ATTR_SCHEDULE_NAME: Final = "schedule_name"
ATTR_SCHEDULE_ENABLED: Final = "enabled"
ATTR_SCHEDULE_DAYS: Final = "days"
ATTR_TIME_BLOCKS: Final = "time_blocks"
ATTR_CONDITIONS: Final = "conditions"
ATTR_TIME: Final = "time"
ATTR_NEXT_BLOCK: Final = "next_block"
ATTR_CURRENT_BLOCK: Final = "current_block"

# Override modes
OVERRIDE_MODE_TIMER: Final = "timer"
OVERRIDE_MODE_NEXT_BLOCK: Final = "next_block"

# Default scheduler settings
DEFAULT_SCHEDULER_ENABLED: Final = True
DEFAULT_OVERRIDE_MODE: Final = OVERRIDE_MODE_NEXT_BLOCK
DEFAULT_OVERRIDE_DURATION: Final = 60  # minutes

# Weekdays
WEEKDAY_MON: Final = "monday"
WEEKDAY_TUE: Final = "tuesday"
WEEKDAY_WED: Final = "wednesday"
WEEKDAY_THU: Final = "thursday"
WEEKDAY_FRI: Final = "friday"
WEEKDAY_SAT: Final = "saturday"
WEEKDAY_SUN: Final = "sunday"

ALL_WEEKDAYS: Final = [
    WEEKDAY_MON,
    WEEKDAY_TUE,
    WEEKDAY_WED,
    WEEKDAY_THU,
    WEEKDAY_FRI,
    WEEKDAY_SAT,
    WEEKDAY_SUN,
]

# Scheduler services
SERVICE_SET_SCHEDULE: Final = "set_schedule"
SERVICE_ENABLE_SCHEDULE: Final = "enable_schedule"
SERVICE_DISABLE_SCHEDULE: Final = "disable_schedule"
