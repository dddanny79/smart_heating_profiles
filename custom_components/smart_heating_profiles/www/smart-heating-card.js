class SmartHeatingCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Please define an entity');
    }
    this.config = config;
  }

  set hass(hass) {
    this._hass = hass;

    if (!this.content) {
      this.content = document.createElement('ha-card');
      this.content.innerHTML = `
        <div class="card-content">
          <div class="loading">Loading...</div>
        </div>
      `;
      this.shadowRoot.appendChild(this.content);
      this._addStyles();
    }

    this._updateContent();
  }

  _addStyles() {
    const style = document.createElement('style');
    style.textContent = `
      ha-card {
        padding: 16px;
        background: var(--ha-card-background, var(--card-background-color, white));
        border-radius: var(--ha-card-border-radius, 12px);
      }

      .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--divider-color, #e0e0e0);
      }

      .header-left {
        display: flex;
        flex-direction: column;
      }

      .card-title {
        font-size: 24px;
        font-weight: 600;
        color: var(--primary-text-color);
        margin: 0;
      }

      .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        margin-top: 6px;
      }

      .status-badge.active {
        background: #4caf5020;
        color: #4caf50;
      }

      .status-badge.override {
        background: #ff980020;
        color: #ff9800;
      }

      .status-badge.disabled {
        background: #9e9e9e20;
        color: #9e9e9e;
      }

      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: currentColor;
      }

      .master-switch {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 20px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
      }

      .master-switch:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      }

      .master-switch.off {
        background: #9e9e9e;
      }

      .next-block {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 20px;
      }

      .next-block-title {
        font-size: 12px;
        opacity: 0.9;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      .next-block-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .next-block-time {
        font-size: 24px;
        font-weight: 700;
      }

      .next-block-temp {
        font-size: 32px;
        font-weight: 700;
      }

      .schedules-container {
        display: grid;
        gap: 16px;
      }

      .schedule-card {
        background: var(--secondary-background-color, #fafafa);
        border-radius: 12px;
        padding: 16px;
        transition: all 0.2s;
      }

      .schedule-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      }

      .schedule-card.disabled {
        opacity: 0.5;
      }

      .schedule-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
      }

      .schedule-name {
        font-size: 18px;
        font-weight: 600;
        color: var(--primary-text-color);
      }

      .schedule-toggle {
        position: relative;
        width: 48px;
        height: 24px;
        background: #ccc;
        border-radius: 12px;
        cursor: pointer;
        transition: background 0.3s;
      }

      .schedule-toggle.on {
        background: var(--primary-color);
      }

      .schedule-toggle::after {
        content: '';
        position: absolute;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: white;
        top: 2px;
        left: 2px;
        transition: transform 0.3s;
      }

      .schedule-toggle.on::after {
        transform: translateX(24px);
      }

      .schedule-days {
        display: flex;
        gap: 4px;
        margin-bottom: 12px;
      }

      .day-badge {
        padding: 4px 8px;
        background: var(--primary-color);
        color: white;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
      }

      .timeline {
        position: relative;
        height: 80px;
        background: linear-gradient(to right, #e3f2fd 0%, #fff3e0 50%, #fce4ec 100%);
        border-radius: 8px;
        margin-top: 12px;
        overflow: hidden;
      }

      .timeline-blocks {
        position: relative;
        height: 100%;
        display: flex;
      }

      .time-block {
        position: absolute;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-left: 2px solid rgba(0,0,0,0.1);
        background: rgba(255,255,255,0.7);
        transition: all 0.2s;
      }

      .time-block:hover {
        background: rgba(255,255,255,0.9);
        z-index: 10;
      }

      .time-block-time {
        font-size: 12px;
        font-weight: 600;
        color: #333;
      }

      .time-block-temp {
        font-size: 16px;
        font-weight: 700;
        color: var(--primary-color);
        margin-top: 4px;
      }

      .current-time-indicator {
        position: absolute;
        top: 0;
        width: 2px;
        height: 100%;
        background: #f44336;
        z-index: 20;
        pointer-events: none;
      }

      .current-time-indicator::before {
        content: '';
        position: absolute;
        top: -4px;
        left: -3px;
        width: 8px;
        height: 8px;
        background: #f44336;
        border-radius: 50%;
      }

      .no-schedules {
        text-align: center;
        padding: 40px;
        color: var(--secondary-text-color);
      }

      .no-schedules-icon {
        font-size: 48px;
        margin-bottom: 12px;
        opacity: 0.3;
      }

      .conditions-list {
        margin-top: 8px;
        padding: 8px;
        background: rgba(0,0,0,0.05);
        border-radius: 6px;
        font-size: 12px;
      }

      .condition-item {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 4px 0;
      }

      .condition-icon {
        color: var(--primary-color);
      }

      @media (max-width: 768px) {
        .schedule-card {
          padding: 12px;
        }

        .timeline {
          height: 60px;
        }

        .time-block-time {
          font-size: 10px;
        }

        .time-block-temp {
          font-size: 14px;
        }
      }

      .loading {
        text-align: center;
        padding: 40px;
        color: var(--secondary-text-color);
      }

      .error {
        color: #f44336;
        padding: 16px;
        text-align: center;
      }
    `;
    this.shadowRoot.appendChild(style);
  }

  _updateContent() {
    if (!this._hass || !this.config) return;

    const entityId = this.config.entity;
    const entity = this._hass.states[entityId];

    if (!entity) {
      this.content.innerHTML = `<div class="error">Entity not found: ${entityId}</div>`;
      return;
    }

    // Get related entities
    const switchEntity = this._hass.states[entityId.replace('climate.', 'switch.') + '_scheduler'];
    const statusSensor = this._hass.states[entityId.replace('climate.', 'sensor.') + '_schedule_status'];
    const nextBlockSensor = this._hass.states[entityId.replace('climate.', 'sensor.') + '_next_schedule'];

    // Get schedule data from attributes
    const schedules = this._getSchedulesFromEntity(entityId);
    const schedulerEnabled = switchEntity?.state === 'on';
    const overrideActive = statusSensor?.attributes?.override_active || false;
    const statusState = statusSensor?.state || 'Unknown';

    this.content.innerHTML = `
      <div class="card-header">
        <div class="header-left">
          <h2 class="card-title">${this.config.name || 'Smart Heating'}</h2>
          ${this._renderStatusBadge(statusState, overrideActive, schedulerEnabled)}
        </div>
        <button class="master-switch ${schedulerEnabled ? 'on' : 'off'}"
                onclick="this.getRootNode().host._toggleScheduler()">
          ${schedulerEnabled ? '✓ Scheduler Active' : '✗ Scheduler Off'}
        </button>
      </div>

      ${nextBlockSensor && schedulerEnabled ? this._renderNextBlock(nextBlockSensor) : ''}

      <div class="schedules-container">
        ${schedules.length > 0 ? schedules.map(s => this._renderSchedule(s)).join('') : this._renderNoSchedules()}
      </div>
    `;
  }

  _renderStatusBadge(status, override, enabled) {
    if (!enabled) {
      return '<div class="status-badge disabled"><span class="status-dot"></span>Disabled</div>';
    }
    if (override) {
      return '<div class="status-badge override"><span class="status-dot"></span>Override Active</div>';
    }
    if (status === 'Active') {
      return '<div class="status-badge active"><span class="status-dot"></span>Schedule Active</div>';
    }
    return '<div class="status-badge"><span class="status-dot"></span>' + status + '</div>';
  }

  _renderNextBlock(sensor) {
    const time = sensor.attributes?.next_block_time || 'Unknown';
    const temp = sensor.state || '?';
    const minutes = sensor.attributes?.minutes_until || 0;

    return `
      <div class="next-block">
        <div class="next-block-title">Next Schedule in ${minutes} minutes</div>
        <div class="next-block-content">
          <div class="next-block-time">🕐 ${time}</div>
          <div class="next-block-temp">${temp}°C</div>
        </div>
      </div>
    `;
  }

  _renderSchedule(schedule) {
    const enabled = schedule.enabled || false;
    const name = schedule.schedule_name || 'Unnamed';
    const days = schedule.days || [];
    const blocks = schedule.time_blocks || [];
    const conditions = schedule.conditions || [];

    const dayAbbrev = {
      'monday': 'Mo', 'tuesday': 'Tu', 'wednesday': 'We',
      'thursday': 'Th', 'friday': 'Fr', 'saturday': 'Sa', 'sunday': 'Su'
    };

    return `
      <div class="schedule-card ${enabled ? '' : 'disabled'}">
        <div class="schedule-header">
          <div class="schedule-name">${name}</div>
          <div class="schedule-toggle ${enabled ? 'on' : ''}"
               onclick="this.getRootNode().host._toggleSchedule('${name}', ${!enabled})"></div>
        </div>

        <div class="schedule-days">
          ${days.map(day => `<div class="day-badge">${dayAbbrev[day] || day.substring(0, 2).toUpperCase()}</div>`).join('')}
        </div>

        ${conditions.length > 0 ? this._renderConditions(conditions) : ''}

        ${this._renderTimeline(blocks)}
      </div>
    `;
  }

  _renderConditions(conditions) {
    return `
      <div class="conditions-list">
        ${conditions.map(c => `
          <div class="condition-item">
            <span class="condition-icon">🔗</span>
            <span>${c.entity_id} = ${c.state}</span>
          </div>
        `).join('')}
      </div>
    `;
  }

  _renderTimeline(blocks) {
    if (!blocks || blocks.length === 0) {
      return '<div style="text-align: center; padding: 20px; color: #999;">No time blocks</div>';
    }

    // Sort blocks by time
    const sortedBlocks = [...blocks].sort((a, b) => a.time.localeCompare(b.time));

    // Calculate current time position
    const now = new Date();
    const currentMinutes = now.getHours() * 60 + now.getMinutes();
    const currentPercent = (currentMinutes / 1440) * 100;

    // Generate timeline
    const timelineHtml = sortedBlocks.map(block => {
      const [hours, minutes] = block.time.split(':').map(Number);
      const totalMinutes = hours * 60 + minutes;
      const leftPercent = (totalMinutes / 1440) * 100;

      return `
        <div class="time-block" style="left: ${leftPercent}%;">
          <div class="time-block-time">${block.time}</div>
          <div class="time-block-temp">${block.temperature}°C</div>
        </div>
      `;
    }).join('');

    return `
      <div class="timeline">
        <div class="timeline-blocks">
          ${timelineHtml}
          <div class="current-time-indicator" style="left: ${currentPercent}%;"></div>
        </div>
      </div>
    `;
  }

  _renderNoSchedules() {
    return `
      <div class="no-schedules">
        <div class="no-schedules-icon">📅</div>
        <div>No schedules configured</div>
        <div style="margin-top: 8px; font-size: 12px;">
          Configure schedules in the integration settings
        </div>
      </div>
    `;
  }

  _getSchedulesFromEntity(entityId) {
    // Get schedules from the dedicated schedules sensor
    const schedulesSensor = this._hass.states[entityId.replace('climate.', 'sensor.') + '_schedules'];

    if (schedulesSensor && schedulesSensor.attributes && schedulesSensor.attributes.schedules) {
      return schedulesSensor.attributes.schedules;
    }

    return [];
  }

  _toggleScheduler() {
    const entityId = this.config.entity;
    const switchEntity = entityId.replace('climate.', 'switch.') + '_scheduler';

    this._hass.callService('switch', 'toggle', {
      entity_id: switchEntity
    });
  }

  _toggleSchedule(scheduleName, enable) {
    const service = enable ? 'enable_schedule' : 'disable_schedule';

    this._hass.callService('smart_heating_profiles', service, {
      entity_id: this.config.entity,
      schedule_name: scheduleName
    });
  }

  getCardSize() {
    return 3;
  }
}

customElements.define('smart-heating-card', SmartHeatingCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'smart-heating-card',
  name: 'Smart Heating Card',
  description: 'A beautiful card for managing Smart Heating Profiles'
});

console.info(
  '%c SMART-HEATING-CARD %c Version 1.0.0 ',
  'color: white; background: #4caf50; font-weight: 700;',
  'color: #4caf50; background: white; font-weight: 700;'
);
