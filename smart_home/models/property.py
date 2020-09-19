from django.db import models
# from django_extensions.db.fields.json import JSONField

from .device_info import DeviceInfo
from .device_type import (
    AlarmDeviceTypeMixin,
    HumiditySensorDeviceTypeMixin,
    IsSecureDeviceTypeMixin,
    LockDeviceTypeMixin,
    TempDeviceTypeMixin,
)


class PropertyController(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)

    def lock(self):
        for device in self.devices.all():
            dev_type = device.info.specific.type
            if isinstance(dev_type, LockDeviceTypeMixin):
                dev_type.lock(device)

    @property
    def is_secure(self):
        for device in self.devices.all():
            dev_type = device.info.specific.type
            if isinstance(dev_type, IsSecureDeviceTypeMixin) and not dev_type.is_secure(device):
                return False
        return True

    @property
    def current_temperatures(self):
        temps = []
        for device in self.devices.all():
            dev_type = device.info.specific.type
            if isinstance(dev_type, TempDeviceTypeMixin):
                temps.append({
                    'location': device.location,
                    'temperature': dev_type.get_current_temperature(device),
                })

        return temps

    @property
    def current_humidity_levels(self):
        humidity_levels = []
        for device in self.devices.all():
            dev_type = device.info.specific.type
            if isinstance(dev_type, HumiditySensorDeviceTypeMixin):
                humidity_levels.append({
                  'location': device.location,
                  'humidity': dev_type.get_current_humidity(device),
                })

        return humidity_levels

    def silence_all_alarms(self):
        for device in self.devices.all():
            dev_type = device.info.specific.type
            if isinstance(dev_type, AlarmDeviceTypeMixin):
                dev_type.silence_alarm(device)

    @property
    def remaining_pin_code_counts(self):
        remaining_counts = []
        for device in FrontDoorLockDevice.objects.filter(controller=self):
            dev_type = device.info.specific.type
            remaining_counts.append({
                'location': device.location,
                'remaining_pin_count': dev_type.max_pin_count - len(device.pin_codes),
            })

        return remaining_counts


class PropertyDevice(models.Model):
    id = models.UUIDField(primary_key=True)
    controller = models.ForeignKey(PropertyController, on_delete=models.CASCADE,
                                   related_name='devices')
    info = models.ForeignKey(DeviceInfo, on_delete=models.PROTECT, related_name='property_devices')
    url = models.URLField()
    location_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ('controller', 'url')


class FrontDoorLockDevice(PropertyDevice):
    base_device = models.OneToOneField(
        PropertyDevice, parent_link=True, on_delete=models.CASCADE,
        related_name='front_door_locks')
    pin_digit_count = models.IntegerField()
    master_pin = models.CharField(max_length=8)
    pin_codes = models.JSONField(default=list)
