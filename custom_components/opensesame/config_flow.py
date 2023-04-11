from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_FILENAME
import voluptuous as vol


class OpenSesameConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}

        if user_input is not None:
            filename = user_input[CONF_FILENAME]
            return self.async_create_entry(
                title="OpenSesame",
                data={CONF_FILENAME: filename},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_FILENAME, default="opensesame_data.json"): str,
                }
            ),
            errors=errors,
        )
