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
