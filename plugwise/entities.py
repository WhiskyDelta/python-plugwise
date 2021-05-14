""" Plugwise Entity Classes."""
import asyncio

from .constants import (
    ATTR_ICON,
    ATTR_ID,
    ATTR_STATE,
    BATTERY,
    COOLING_ICON,
    CURRENT_TEMP,
    DEVICE_STATE,
    DHW_COMF_MODE,
    DHW_STATE,
    EL_CONSUMED,
    EL_CONSUMED_INTERVAL,
    EL_CONSUMED_OFF_PEAK_CUMULATIVE,
    EL_CONSUMED_OFF_PEAK_INTERVAL,
    EL_CONSUMED_OFF_PEAK_POINT,
    EL_CONSUMED_PEAK_CUMULATIVE,
    EL_CONSUMED_PEAK_INTERVAL,
    EL_CONSUMED_PEAK_POINT,
    EL_PRODUCED,
    EL_PRODUCED_INTERVAL,
    EL_PRODUCED_OFF_PEAK_CUMULATIVE,
    EL_PRODUCED_OFF_PEAK_INTERVAL,
    EL_PRODUCED_OFF_PEAK_POINT,
    EL_PRODUCED_PEAK_CUMULATIVE,
    EL_PRODUCED_PEAK_INTERVAL,
    EL_PRODUCED_PEAK_POINT,
    FLAME_ICON,
    FLAME_STATE,
    FLOW_OFF_ICON,
    FLOW_ON_ICON,
    GAS_CONSUMED_CUMULATIVE,
    GAS_CONSUMED_INTERVAL,
    HEATING_ICON,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_OFF,
    IDLE_ICON,
    ILLUMINANCE,
    INTENDED_BOILER_TEMP,
    LOCATIONS,
    LOCK,
    MOD_LEVEL,
    NET_EL_CUMULATIVE,
    NET_EL_POINT,
    NO_NOTIFICATION_ICON,
    NOTIFICATION_ICON,
    OUTDOOR_TEMP,
    PRESET_AWAY,
    PW_NOTIFICATION,
    RELAY,
    RETURN_TEMP,
    RULES,
    SEVERITIES,
    SLAVE_BOILER_STATE,
    TARGET_TEMP,
    TEMP_DIFF,
    VALVE_POS,
    WATER_PRESSURE,
    WATER_TEMP,
)
from .smile import Smile


class GW_B_Sensor:
    """ Represent the Plugwise Smile/Stretch binary_sensor."""

    def __init__(self, api, dev_id, binary_sensor):
        """Initialize the Gateway."""
        self._api = api
        self._binary_sensor = binary_sensor
        self._dev_id = dev_id
        self._attributes = {}
        self._icon = None
        self._is_on = False
        self._message = None

    @property
    def extra_state_attributes(self):
        """Gateway binary_sensor extra state attributes."""
        return None if self._attributes == {} else self._attributes

    @property
    def is_on(self):
        """Gateway binary_sensor state."""
        return self._is_on

    @property
    def icon(self):
        """Gateway binary_sensor icon."""
        return self._icon

    @property
    def notification(self):
        """Plugwise Notification message."""
        return self._message

    def update_data(self):
        """Handle update callbacks."""
        data = self._api.gw_devices[self._dev_id]

        for key, value in data.items():
            if key != "binary_sensors":
                continue

            for idx, item in enumerate(data["binary_sensors"]):
                if item[ATTR_ID] != self._binary_sensor:
                    continue

                self._is_on = item[ATTR_STATE]
                if self._binary_sensor == "dhw_state":
                    self._icon = FLOW_ON_ICON if self._is_on else FLOW_OFF_ICON
                if (
                    self._binary_sensor == "flame_state"
                    or self._binary_sensor == "slave_boiler_state"
                ):
                    self._icon = FLAME_ICON if self._is_on else IDLE_ICON

                if self._binary_sensor != "plugwise_notification":
                    continue

                self._icon = NOTIFICATION_ICON if self._is_on else NO_NOTIFICATION_ICON
                notify = self._api.notifications
                self._message = None
                for severity in SEVERITIES:
                    self._attributes[f"{severity.upper()}_msg"] = []
                if notify != {}:
                    for notify_id, details in notify.items():
                        for msg_type, msg in details.items():
                            if msg_type not in SEVERITIES:
                                msg_type = "other"

                            self._attributes[f"{msg_type.upper()}_msg"].append(msg)
                            self._message = (
                                f"{msg_type.title()}: {msg}",
                                "Plugwise Notification:",
                                f"plugwise.{notify_id}",
                            )


class GW_Thermostat:
    """Represent a Plugwise Thermostat Device."""

    def __init__(self, api, dev_id):
        """Initialize the Thermostat."""

        self._api = api
        self._compressor_state = None
        self._cooling_state = None
        self._dev_id = dev_id
        self._extra_state_attributes = None
        self._get_presets = None
        self._heating_state = None
        self._hvac_mode = None
        self._last_active_schema = None
        self._preset_mode = None
        self._preset_modes = None
        self._schedule_temp = None
        self._schema_names = None
        self._schema_status = None
        self._selected_schema = None
        self._setpoint = None
        self._smile_class = None
        self._temperature = None

        self._active_device = self._api.active_device_present
        self._heater_id = self._api.heater_id
        self._sm_thermostat = self._api.single_master_thermostat()

    @property
    def compressor_state(self):
        """Compressor state."""
        return self._compressor_state

    @property
    def cooling_state(self):
        """Cooling state."""
        return self._cooling_state

    @property
    def heating_state(self):
        """Heating state."""
        return self._heating_state

    @property
    def hvac_mode(self):
        """Climate active HVAC mode."""
        return self._hvac_mode

    @property
    def presets(self):
        """Climate list of presets."""
        return self._get_presets

    @property
    def preset_mode(self):
        """Climate active preset mode."""
        return self._preset_mode

    @property
    def preset_modes(self):
        """Climate preset modes."""
        return self._preset_modes

    @property
    def last_active_schema(self):
        """Climate last active schema."""
        return self._last_active_schema

    @property
    def current_temperature(self):
        """Climate current measured temperature."""
        return self._temperature

    @property
    def target_temperature(self):
        """Climate target temperature."""
        return self._setpoint

    @property
    def schedule_temperature(self):
        """Climate target temperature."""
        return self._schedule_temp

    @property
    def extra_state_attributes(self):
        """Climate extra state attributes."""
        return self._extra_state_attributes

    def update_data(self):
        """Handle update callbacks."""
        data = self._api.gw_devices[self._dev_id]

        # current & target_temps, heater_central data when required
        s_list = data["sensors"]
        for idx, item in enumerate(s_list):
            if item[ATTR_ID] == "temperature":
                self._temperature = s_list[idx][ATTR_STATE]
            if item[ATTR_ID] == "setpoint":
                self._setpoint = s_list[idx][ATTR_STATE]
        self._schedule_temp = data.get("schedule_temperature")
        if self._active_device:
            hc_data = self._api.gw_devices[self._heater_id]
            self._compressor_state = hc_data.get("compressor_state")
            if self._sm_thermostat:
                self._cooling_state = hc_data.get("cooling_state")
                self._heating_state = hc_data.get("heating_state")

        # hvac mode
        self._hvac_mode = HVAC_MODE_AUTO
        if "selected_schedule" in data:
            self._selected_schema = data.get("selected_schedule")
            self._schema_status = False
            if self._selected_schema is not None:
                self._schema_status = True

        self._last_active_schema = data.get("last_used")

        if not self._schema_status:
            if self._preset_mode == PRESET_AWAY:
                self._hvac_mode = HVAC_MODE_OFF
            else:
                self._hvac_mode = HVAC_MODE_HEAT
                if self._compressor_state is not None:
                    self._hvac_mode = HVAC_MODE_HEAT_COOL

        # preset modes
        self._get_presets = data.get("presets")
        if self._get_presets:
            self._preset_modes = list(self._get_presets)

        # preset mode
        self._preset_mode = data.get("active_preset")

        # extra state attributes
        attributes = {}
        self._schema_names = data.get("available_schedules")
        self._selected_schema = data.get("selected_schedule")
        if self._schema_names:
            attributes["available_schemas"] = self._schema_names
        if self._selected_schema:
            attributes["selected_schema"] = self._selected_schema
        self._extra_state_attributes = attributes


class GW_Sensor:
    """Represent an external Auxiliary Device."""

    def __init__(self, api, dev_id, sensor):
        """Initialize the Thermostat."""
        self._api = api
        self._dev_id = dev_id
        self._icon = None
        self._sensor = sensor
        self._state = None

    @property
    def icon(self):
        """Gateway binary_sensor/sensor/switch icon."""
        return self._icon

    @property
    def state(self):
        """Gateway binary_sensor state."""
        return self._state

    def update_data(self):
        """Handle update callbacks."""
        data = self._api.gw_devices[self._dev_id]

        for key, value in data.items():
            if key != "sensors":
                continue

            for idx, item in enumerate(data["sensors"]):
                if item[ATTR_ID] != self._sensor:
                    continue

                self._state = item[ATTR_STATE]
                self._icon = item[ATTR_ICON]
                if self._sensor == DEVICE_STATE:
                    self._icon = IDLE_ICON
                    if sens[ATTR_STATE] == "dhw-heating":
                        self._icon = HEATING_ICON
                    if sens[ATTR_STATE] == "heating":
                        self._icon = HEATING_ICON
                    if sens[ATTR_STATE] == "dhw and heating":
                        self._icon = HEATING_ICON
                    if sens[ATTR_STATE] == "COOLING_ICON":
                        self._icon = COOLING_ICON
                    if sens[ATTR_STATE] == "dhw and cooling":
                        self._icon = COOLING_ICON
