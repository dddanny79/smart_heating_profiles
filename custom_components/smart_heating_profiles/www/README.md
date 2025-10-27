# Smart Heating Card

Beautiful, user-friendly dashboard card for Smart Heating Profiles integration.

## Features

- 📅 Visual timeline showing all time blocks
- 🎨 Beautiful, modern design with smooth animations
- 🔄 Real-time schedule status updates
- 📱 Responsive (works on mobile & desktop)
- ⚡ Quick toggle switches for schedules
- 🕐 Live "current time" indicator on timeline
- 🎯 Next block countdown
- 🔗 Condition indicators

## Installation

### Method 1: Manual Installation

1. **Copy the card file:**
   ```bash
   cp www/smart-heating-card.js /config/www/
   ```

2. **Add the resource in Home Assistant:**
   - Go to Settings → Dashboards → Resources
   - Click "+ Add Resource"
   - URL: `/local/smart-heating-card.js`
   - Resource type: `JavaScript Module`
   - Click "Create"

3. **Restart Home Assistant** (or reload Lovelace)

### Method 2: HACS (Future)

*Coming soon: Will be available via HACS custom repository*

## Usage

### Basic Configuration

Add the card to your dashboard:

```yaml
type: custom:smart-heating-card
entity: climate.your_smart_heating_profile
```

### Full Configuration

```yaml
type: custom:smart-heating-card
entity: climate.your_smart_heating_profile
name: Living Room Heating
```

### Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `type` | string | Yes | - | Must be `custom:smart-heating-card` |
| `entity` | string | Yes | - | Your climate entity ID |
| `name` | string | No | Auto | Custom name for the card header |

## Card Features Explained

### Header Section
- **Card Title**: Shows the name of your heating profile
- **Status Badge**:
  - 🟢 Active - Schedule is running
  - 🟠 Override - Manual override active
  - ⚪ Disabled - Scheduler is off
- **Master Switch**: Quick toggle for entire scheduler

### Next Block Info
- Shows upcoming schedule change
- Displays time and temperature
- Countdown in minutes

### Schedule Cards

Each schedule shows:

- **Schedule Name** with toggle switch
- **Active Days** as color-coded badges
- **Conditions** (if configured)
- **Timeline** with:
  - Time blocks showing temperature changes
  - Visual gradient background
  - Red line showing current time
  - Hover effects for details

## Screenshots

### Desktop View
The card displays all schedules in a grid layout with:
- Large, readable fonts
- Color-coded time blocks
- Smooth hover animations

### Mobile View
Automatically adapts to:
- Smaller screens
- Touch-friendly controls
- Optimized spacing

## Timeline Explained

The timeline shows a 24-hour view:
- **Left** (00:00) → **Right** (24:00)
- **Vertical lines**: Time blocks
- **Numbers**: Temperatures at each time
- **Red line**: Current time
- **Background gradient**: Visual time-of-day indicator
  - Blue (morning)
  - Yellow (afternoon)
  - Pink (evening/night)

## Interactivity

### Toggle Schedule
Click the switch next to any schedule name to enable/disable it.

### Toggle Master Scheduler
Click the master switch button in the header to turn the entire scheduler on/off.

### View Details
Hover over time blocks to see them highlighted.

## Troubleshooting

### Card not showing

1. **Check entity ID:**
   ```yaml
   # Make sure your entity exists
   entity: climate.smart_heating_profile  # Use YOUR entity ID
   ```

2. **Verify resource is loaded:**
   - Settings → Dashboards → Resources
   - Should see `/local/smart-heating-card.js`

3. **Clear browser cache:**
   - Press `Ctrl+F5` (Windows/Linux)
   - Or `Cmd+Shift+R` (Mac)

### Schedules not appearing

The card needs this sensor to exist:
```
sensor.<your_name>_schedules
```

This sensor is automatically created by the integration when you configure schedules via the integration settings.

### Toggles not working

Make sure these entities exist:
- `switch.<your_name>_scheduler` - Master switch
- Service `smart_heating_profiles.enable_schedule` available
- Service `smart_heating_profiles.disable_schedule` available

## Example Dashboard Layout

### Single Card
```yaml
type: custom:smart-heating-card
entity: climate.living_room_heating
```

### With Other Cards
```yaml
type: vertical-stack
cards:
  - type: custom:smart-heating-card
    entity: climate.living_room_heating

  - type: entities
    entities:
      - sensor.living_room_heating_schedule_status
      - sensor.living_room_heating_next_schedule
      - switch.living_room_heating_scheduler
```

### Grid Layout
```yaml
type: grid
columns: 2
square: false
cards:
  - type: custom:smart-heating-card
    entity: climate.living_room_heating
  - type: custom:smart-heating-card
    entity: climate.bedroom_heating
```

## Styling

The card uses CSS variables from your Home Assistant theme:

- `--primary-color`: Used for active states, buttons
- `--primary-text-color`: Main text color
- `--secondary-text-color`: Muted text
- `--ha-card-background`: Card background
- `--divider-color`: Borders and dividers

### Custom Styling (Advanced)

Use `card-mod` to customize further:

```yaml
type: custom:smart-heating-card
entity: climate.living_room_heating
card_mod:
  style: |
    ha-card {
      --primary-color: #ff6b6b !important;
    }
```

## Updates

To update the card:

1. Replace `www/smart-heating-card.js` with new version
2. Clear browser cache (`Ctrl+F5`)
3. Hard refresh your dashboard

## Support

If you encounter issues:

1. Check Home Assistant logs
2. Open browser console (F12) for JavaScript errors
3. Report issues at: https://github.com/dddanny79/smart_heating_profiles/issues

## Credits

Part of the Smart Heating Profiles integration.

## Changelog

### v1.0.0 (Initial Release)
- Visual timeline for time blocks
- Schedule toggle switches
- Master scheduler control
- Next block countdown
- Condition indicators
- Responsive design
- Real-time updates
