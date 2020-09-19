from django.db import models
from staticmodel import StaticModel
from staticmodel.django.fields import StaticModelCharField

from .manufacturer import Manufacturer
from .device_type import (
    FrontDoorLockType,
    MultiFunctionType,
    SensorType,
    SwitchType,
    ThermostatType,
    TypeMixin,
)


class StaticModelInfoTypeField(StaticModelCharField):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'max_length': 20,
            'value_field_name': 'code',
            'display_field_name': 'name',
        })
        super(StaticModelInfoTypeField, self).__init__(*args, **kwargs)


class DeviceInfoType(TypeMixin, StaticModel):
    _field_names = TypeMixin._field_names + ('base_device_info_field',)
    SWITCH = ('switch', 'Switch', 'switch_info')
    THERMOSTAT = ('thermostat', 'Thermostat', 'thermostat_info')
    FRONT_DOOR_LOCK = ('front_door_lock', 'Front Door Lock', 'front_door_lock_info')
    SENSOR = ('sensor', 'Sensor', 'sensor_info')
    MULTI_FUNCTION = ('multi_function', 'Multi-Function', 'multi_function_info')


class DeviceInfo(models.Model):
    """
    Base model for specific device types via multi-table inheritance.
    """
    id = models.UUIDField(primary_key=True)
    info_type = StaticModelInfoTypeField(static_model=DeviceInfoType)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT,
                                     related_name='devices')
    model_code = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    # Additional device fields like cost, etc.

    @property
    def specific(self):
        return getattr(self, self.info_type.base_device_info_field)


class SwitchInfo(DeviceInfo):
    base_device_info = models.OneToOneField(
        DeviceInfo, parent_link=True, on_delete=models.CASCADE,
        related_name=DeviceInfoType.SWITCH.base_device_info_field)
    type = StaticModelInfoTypeField(static_model=SwitchType)


class SensorInfo(DeviceInfo):
    base_device_info = models.OneToOneField(
        DeviceInfo, parent_link=True, on_delete=models.CASCADE,
        related_name=DeviceInfoType.SENSOR.base_device_info_field)
    type = StaticModelInfoTypeField(static_model=SensorType)


class ThermostatInfo(DeviceInfo):
    base_device_info = models.OneToOneField(
        DeviceInfo, parent_link=True, on_delete=models.CASCADE,
        related_name=DeviceInfoType.THERMOSTAT.base_device_info_field)
    type = StaticModelInfoTypeField(static_model=ThermostatType)


class FrontDoorLockInfo(DeviceInfo):
    base_device_info = models.OneToOneField(
        DeviceInfo, parent_link=True, on_delete=models.CASCADE,
        related_name=DeviceInfoType.FRONT_DOOR_LOCK.base_device_info_field)
    type = StaticModelInfoTypeField(static_model=FrontDoorLockType)


class MultiFunctionInfo(DeviceInfo):
    base_device_info = models.OneToOneField(
        DeviceInfo, parent_link=True, on_delete=models.CASCADE,
        related_name=DeviceInfoType.MULTI_FUNCTION.base_device_info_field)
    type = StaticModelInfoTypeField(static_model=MultiFunctionType)
