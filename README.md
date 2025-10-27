# Smart Heating Profiles

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

A Home Assistant custom integration for intelligent heating profile management.

## Features

- 🎯 **Smart Heating Profiles**: Create and manage multiple heating profiles for different scenarios
- 📅 **Automated Scheduling**: Set up time-based heating schedules with multiple time blocks
- 🔄 **Conditional Schedules**: Activate schedules based on presence sensors or other conditions
- ⏱️ **Flexible Override Modes**: Choose between timer-based or next-block resume after manual changes
- 📊 **Beautiful Dashboard Card**: Visual timeline interface for managing schedules
- ⚡ **Integration Ready**: Works seamlessly with existing Home Assistant climate entities

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
- Set up automatic switching between profiles with conditions
- Monitor and optimize your heating efficiency
- Integrate with other Home Assistant automations

### Dashboard Card

The integration includes a beautiful custom Lovelace card for managing your heating schedules:

1. **Automatic Installation**: The card is installed automatically with the integration
2. **Register Resource** (if needed):
   - Go to Settings → Dashboards → Resources
   - Click "+ Add Resource"
   - URL: `/hacsfiles/smart_heating_profiles/smart-heating-card.js`
   - Resource type: JavaScript Module
3. **Add to Dashboard**:
   ```yaml
   type: custom:smart-heating-card
   entity: climate.your_smart_heating_profile
   ```

See `custom_components/smart_heating_profiles/www/README.md` for detailed card documentation and examples.

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

[buymecoffee]: https://www.buymeacoffee.com/dddanny79
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/dddanny79/smart_heating_profiles.svg?style=for-the-badge
[commits]: https://github.com/dddanny79/smart_heating_profiles/commits/main
[license-shield]: https://img.shields.io/github/license/dddanny79/smart_heating_profiles.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-dddanny79-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/dddanny79/smart_heating_profiles.svg?style=for-the-badge
[releases]: https://github.com/dddanny79/smart_heating_profiles/releases