import logging
from datetime import datetime as dt
from typing import Any, Callable, Dict, List, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, PARCEL_DATABASE
from .parcel_database import ParcelDatabase

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: Callable
) -> None:
    parcel_database: ParcelDatabase = hass.data[DOMAIN][entry.entry_id][PARCEL_DATABASE]

    async def async_update_data() -> Dict[str, Any]:
        return {
            "waiting_count": parcel_database.count_unchecked_parcels(),
            "waiting_list": ", ".join(parcel_database.get_unchecked_parcels()),
        }

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensor",
        update_method=async_update_data,
        update_interval=None,
    )

    # Fetch the initial data
    await coordinator.async_refresh()
    # Store the coordinator in hass.data
    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    result_sensor = OpenSesameResultSensor(parcel_database)

    # Store the reference to the result sensor
    hass.data[DOMAIN][entry.entry_id]["result_sensor"] = result_sensor

    async_add_entities(
        [
            OpenSesameWaitingCountSensor(coordinator, parcel_database),
            OpenSesameWaitingListSensor(coordinator, parcel_database),
            result_sensor,
        ]
    )


class OpenSesameWaitingCountSensor(CoordinatorEntity, Entity):
    def __init__(
        self, coordinator: DataUpdateCoordinator, parcel_database: ParcelDatabase
    ) -> None:
        super().__init__(coordinator)
        self._parcel_database = parcel_database

    @property
    def name(self) -> str:
        return "OpenSesame Waiting Count"

    @property
    def unique_id(self) -> str:
        return "opensesame_waiting_count"

    @property
    def state(self) -> Optional[str]:
        return self.coordinator.data["waiting_count"]


class OpenSesameWaitingListSensor(CoordinatorEntity, Entity):
    def __init__(
        self, coordinator: DataUpdateCoordinator, parcel_database: ParcelDatabase
    ) -> None:
        super().__init__(coordinator)
        self._parcel_database = parcel_database

    @property
    def name(self) -> str:
        return "OpenSesame Waiting List"

    @property
    def unique_id(self) -> str:
        return "opensesame_waiting_list"

    @property
    def state(self) -> Optional[str]:
        return self.coordinator.data["waiting_list"]


class OpenSesameResultSensor(Entity):
    def __init__(self, parcel_database: ParcelDatabase) -> None:
        self._parcel_database = parcel_database
        self._state = "not-checked"

    @property
    def name(self) -> str:
        return "OpenSesame Result"

    @property
    def unique_id(self) -> str:
        return "opensesame_result"

    @property
    def state(self) -> Optional[str]:
        return self._state

    def update_state(self, state, parcel_number):
        self._state = state
        self._parcel_number = parcel_number
        self.async_write_ha_state()

    @property
    def state(self) -> Optional[str]:
        return self._state

    @property
    def extra_state_attributes(self) -> Optional[Dict[str, Any]]:
        return {"number": self._parcel_number} if self._parcel_number else {}
