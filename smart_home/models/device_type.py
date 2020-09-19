from staticmodel import StaticModel


class SettingName:
    AC_ENABLED = 'ac_enabled'
    ALARM_SILENCE_DURATION = 'alarm_silence_time'
    FAN_RUN_TIME = 'fan_run_time'
    HEATER_ENABLED = 'heater_enabled'
    IS_ON = 'is_on'
    IS_SECURE = 'is_secure'
    MAX_TEMP = 'max_temp'
    MIN_TEMP = 'min_temp'
    PIN_CODES = 'pin_codes'
    TARGET_HUMIDITY = 'target_humidity'
    VOLUME = 'volume'


class CommandName:
    LOCK = 'lock'
    SILENCE_ALARM = 'silence_alarm'
    TOGGLE_ALARM = 'toggle_alarm'
    TOGGLE_FAN = 'toggle_fan'
    TOGGLE_TEMP_UNIT = 'toggle_temp_unit'
    TURN_OFF = 'turn_off'
    TURN_ON = 'turn_on'
    TURN_ON_FAN = 'turn_on_fan'
    UNLOCK = 'unlock'


class TypeMixin:
    _field_names = ('code', 'name')


class DeviceTypeMixin(TypeMixin):
    def send_command(self, device, command):
        # Send the command to the device,
        # using configuration details provided by 'device'...
        pass

    def get_setting(self, device, setting_name):
        # Request setting value from device,
        # using configuration details provided by 'device'...
        return f'{setting_name}_value'

    def set_setting(self, device, setting_name, value):
        # Set the given setting value on the device,
        # using configuration details provided by 'device'...
        pass


class SwitchDeviceTypeMixin(DeviceTypeMixin):
    def get_is_on(self, device):
        return self.get_setting(device, SettingName.IS_ON)

    def turn_on(self, device):
        self.send_command(device, CommandName.TURN_ON)

    def turn_off(self, device):
        self.send_command(device, CommandName.TURN_OFF)


class SwitchType(SwitchDeviceTypeMixin, StaticModel):
    SWITCH = ('switch', 'Switch')


class TempDeviceTypeMixin(SwitchDeviceTypeMixin):
    def toggle_temp_unit(self, device):
        self.send_command(device, CommandName.TOGGLE_TEMP_UNIT)

    def get_current_temperature(self, device):
        return SensorType.TEMP.read(device)


class HumiditySensorDeviceTypeMixin(SwitchDeviceTypeMixin):
    def get_current_humidity(self, device):
        return SensorType.HUMIDITY.read(device)


class IsSecureDeviceTypeMixin(SwitchDeviceTypeMixin):
    def is_secure(self, device):
        return self.get_setting(device, SettingName.IS_SECURE)


class LockDeviceTypeMixin(SwitchDeviceTypeMixin):
    def lock(self, device):
        self.send_command(device, CommandName.LOCK)

    def unlock(self, device):
        self.send_command(device, CommandName.UNLOCK)


class FloodSensorDeviceTypeMixin(SwitchDeviceTypeMixin):
    def get_flood_status(self, device):
        return SensorType.FLOOD.read(device)


class AlarmDeviceTypeMixin(SwitchDeviceTypeMixin):
    def toggle_alarm(self, device):
        self.set_setting(device, SettingName.ALARM_SILENCE_DURATION, None)
        self.send_command(device, CommandName.TOGGLE_ALARM)

    def silence_alarm(self, device, time=None):
        self.set_setting(device, SettingName.ALARM_SILENCE_DURATION, time)
        self.send_command(device, CommandName.SILENCE_ALARM)

    def silence_alarm_temporarily(self, device):
        self.silence_alarm(device, device.alarm_silence_duration)

    def set_volume(self, device, value):
        if value < 1:
            value = 1
        elif value > 10:
            value = 10
        self.set_setting(device, SettingName.VOLUME, value)


class SensorType(SwitchDeviceTypeMixin, StaticModel):
    _field_names = SwitchDeviceTypeMixin._field_names + ('prop_names',)
    HUMIDITY = ('humidity', 'Humidity', ('humidity',))
    FLOOD = ('flood', 'Flood', ('is_flooded',))
    CO = ('co', 'Carbon Monoxide', ('co_levels',))
    SMOKE = ('smoke', 'Smoke', ('smoke_levels',))

    def read(self, device):
        # Request sensor reading from device,
        # using configuration details provided by 'device'...
        return {prop_name: f'{prop_name}_value' for prop_name in self.prop_names}


class TempSensorType(TempDeviceTypeMixin, SensorType):
    TEMP = ('temp', 'Temperature', ('temp', 'temp_unit'))


class WindowSensorType(IsSecureDeviceTypeMixin, SensorType):
    WINDOW = ('window', 'Window', ('is_open',))

    def is_secure(self, device):
        return not self.read(device)['is_open']


class ThermostatType(TempDeviceTypeMixin, StaticModel):
    BASIC = ('basic', 'Basic')

    _HUMIDITY_FEATURE_ERROR = 'The {} thermostat does not have a humidity feature.'

    def set_max_temp(self, device, temp_value):
        self.set_setting(device, SettingName.MAX_TEMP, temp_value)

    def get_max_temp(self, device):
        return self.get_setting(device, SettingName.MAX_TEMP)

    def set_min_temp(self, device, temp_value):
        self.set_setting(device, SettingName.MIN_TEMP, temp_value)

    def get_min_temp(self, device):
        return self.get_setting(device, SettingName.MIN_TEMP)

    def get_ac_enabled(self, device):
        return self.get_setting(device, SettingName.AC_ENABLED)

    def get_heater_enabled(self, device):
        return self.get_setting(device, SettingName.HEATER_ENABLED)

    def toggle_temp_unit(self, device):
        self.send_command(device, CommandName.TOGGLE_TEMP_UNIT)

    def toggle_fan(self, device):
        self.set_setting(device, SettingName.FAN_RUN_TIME, None)
        self.send_command(device, CommandName.TOGGLE_FAN)

    def turn_on_fan(self, device, time=None):
        self.set_setting(device, SettingName.FAN_RUN_TIME, time)
        self.send_command(device, CommandName.TURN_ON_FAN)

    def turn_on_fan_temporarily(self, device):
        self.turn_on_fan(device, device.fan_run_time)

    def get_current_temp(self, device):
        return SensorType.TEMP.read(device)


class HumidityThermostatType(HumiditySensorDeviceTypeMixin, ThermostatType):
    PLUS_HUMIDITY = ('plus_humidity', 'Plus Humidity')

    def set_target_humidity(self, device, value):
        self.set_setting(device, SettingName.TARGET_HUMIDITY, value)

    def get_target_humidity(self, device):
        self.get_setting(device, SettingName.TARGET_HUMIDITY)


class FrontDoorLockType(LockDeviceTypeMixin, IsSecureDeviceTypeMixin, StaticModel):
    _field_names = DeviceTypeMixin._field_names + ('max_pin_count',)
    PIN_LIMIT_25 = ('pin_limit_25', 'PIN Limit 25', 25)
    PIN_LIMIT_100 = ('pin_limit_100', 'PIN Limit 25', 100)

    def set_pin_codes(self, device):
        if len(device.pin_codes) > (self.max_pin_count - 1):
            raise ValueError(f'Maximum PIN count of {self.max_pin_count} exceeded')
        if len(device.master_pin) != device.pin_digit_count:
            raise ValueError(f'Master PIN is not {device.pin_digit_count} digits.')
        if not all(len(pin) == device.pin_digit_count for pin in device.pin_codes):
            raise ValueError(f'All PIN codes must be {device.pin_digit_count} digits.')

        self.set_setting(device, SettingName.PIN_CODES, [device.master_pin] +
                         device.pin_codes)


class MultiFunctionType(SwitchDeviceTypeMixin, StaticModel):
    pass


class HumFldTempAlarmType(HumiditySensorDeviceTypeMixin, FloodSensorDeviceTypeMixin,
                          TempDeviceTypeMixin, AlarmDeviceTypeMixin,
                          MultiFunctionType):
    HUM_FLD_TEMP_ALM = ('hum_fld_temp_alm', 'Humidity, Flood, Temp, Alarm')


class CoSmokeDetectorType(AlarmDeviceTypeMixin, MultiFunctionType):
    CO_SMOKE_DETECTOR = ('co_smoke_detector', 'Carbon Monoxide & Smoke Detector')

    def get_co_levels(self, device):
        return SensorType.CO.read(device)

    def get_smoke_levels(self, device):
        return SensorType.SMOKE.read(device)
