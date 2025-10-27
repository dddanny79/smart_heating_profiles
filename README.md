# Smart Heating Profiles

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

A Home Assistant custom integration for intelligent heating profile management.

## Features

- **Smart Heating Profiles**: Create and manage multiple heating profiles for different scenarios
- **Automated Scheduling**: Set up time-based heating schedules
- **Energy Optimization**: Optimize heating based on occupancy and weather conditions
- **Integration Ready**: Works seamlessly with existing Home Assistant climate entities

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository to HACS as a custom repository
3. Install "Smart Heating Profiles" through HACS
4. Restart Home Assistant
5. Add the integration through the UI

### Manual Installation

1. Download the latest release from the [releases page][releases]
2. Extract the files to your `custom_components/smart_heating_profiles/` directory
3. Restart Home Assistant
4. Add the integration through the UI

## Configuration

The integration can be configured through the Home Assistant UI:

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "Smart Heating Profiles"
4. Follow the configuration steps

## Usage

After installation and configuration, you can:

- Create heating profiles for different times of day
- Set up automatic switching between profiles
- Monitor and optimize your heating efficiency
- Integrate with other Home Assistant automations

## Development

This integration is built with:

- Python 3.11+
- Home Assistant Core
- Modern async/await patterns

### Contributing

Contributions are welcome! Please read the contributing guidelines and submit pull requests.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

[buymecoffee]: https://www.buymeacoffee.com/username
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/username/smart-heating-profiles.svg?style=for-the-badge
[commits]: https://github.com/username/smart-heating-profiles/commits/main
[license-shield]: https://img.shields.io/github/license/username/smart-heating-profiles.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-username-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/username/smart-heating-profiles.svg?style=for-the-badge
[releases]: https://github.com/username/smart-heating-profiles/releases