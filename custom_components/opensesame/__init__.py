import logging
import datetime
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, PARCEL_DATABASE
from .parcel_database import ParcelDatabase

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})

    parcel_database = ParcelDatabase(
        "custom_components/opensesame/parcels.json")
    hass.data[DOMAIN][entry.entry_id] = {PARCEL_DATABASE: parcel_database}

    async def async_add_parcel(call):
        # parcel_number = call.data["number"]
        parcel_number = call.data.get("number")
        if isinstance(parcel_number, int):
            parcel_number = str(parcel_number)
        parcel_database.add_parcel(parcel_number)
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id].get("coordinator")
            if coordinator:
                await coordinator.async_request_refresh()

    async def async_check_parcel(call):
        # parcel_number = call.data["number"]
        parcel_number = call.data.get("number")

        if isinstance(parcel_number, int):
            parcel_number = str(parcel_number)
        result = parcel_database.check_parcel(parcel_number)

        for entry_id in hass.data[DOMAIN]:
            result_sensor = hass.data[DOMAIN][entry_id].get("result_sensor")

            if result:
                if result_sensor:
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    result_sensor.update_state(current_time, parcel_number)
            else:
                if result_sensor:
                    result_sensor.update_state(None, None)

        return result

    async def async_del_parcel(call):
        # parcel_number = call.data["number"]
        parcel_number = call.data.get("number")

        if isinstance(parcel_number, int):
            parcel_number = str(parcel_number)

        parcel_database.del_parcel(parcel_number)
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id].get("coordinator")
            if coordinator:
                await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, "add_parcel", async_add_parcel)
    hass.services.async_register(DOMAIN, "check_parcel", async_check_parcel)
    hass.services.async_register(DOMAIN, "del_parcel", async_del_parcel)

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.services.async_remove(DOMAIN, "add_parcel")
    hass.services.async_remove(DOMAIN, "check_parcel")
    hass.services.async_remove(DOMAIN, "del_parcel")
    return True
