"""Adds config flow for electrasmartclimatesensor."""
from collections import OrderedDict
import logging
import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class ElectraSmartClimateSensorFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for electrasmartclimatesensor."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize."""
        self._phone = Optional[str] = None
        self._imei = Optional[str] = None
        self._token = Optional[str] = None
        # self._ac_ids = Optional[list] = None
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}
        if user_input is not None:
            valid = await self._validate_template(user_input["template"])
            if valid:
                return self.async_create_entry(
                    title=user_input["name"], data=user_input
                )
            else:
                self._errors["base"] = "template"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""

        # Defaults
        name = ""
        phone = ""
        imei = ""
        token = ""

        if user_input is not None:
            if "name" in user_input:
                name = user_input["name"]
            if "phone" in user_input:
                template = user_input["phone"]
            if "imei" in user_input:
                device_class = user_input["imei"]

        data_schema = OrderedDict()
        data_schema[vol.Required("name", default=name)] = str
        data_schema[vol.Required("template", default=template)] = str
        data_schema[vol.Optional("device_class", default=device_class)] = str
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(data_schema), errors=self._errors
        )

    async def _validate_template(self, template):
        """Return true if template is valid."""
        try:
            templater.Template(template, self.hass).async_render()
            return True
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error(exception)
            pass
        return False