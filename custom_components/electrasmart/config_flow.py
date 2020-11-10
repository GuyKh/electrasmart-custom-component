"""Adds config flow for electrasmartclimatesensor."""
from collections import OrderedDict
import logging
import re
import voluptuous as vol

from homeassistant import config_entries

from .const import { DOMAIN }

from electrasmart import { send_otp_request, get_otp_token, get_devices, AC, ElectraAPI }

_LOGGER = logging.getLogger(__name__)


async def is_phone_valid(
    data,
):
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    Request configuration steps from the user.
    """

    phone = data.get("phone")
    if phone is not None:
        phonePattern = "[0-9]{10}"
        m = re.match(phonePattern, phone)

        if m:
            return {
                "title": "phone",
                "phone": data.get("phone")
            }
        else:
            return None
    return None

async def is_otp_valid(
    data,
):
    """Validate the user input allows us to connect.
    Data has the keys from DATA_SCHEMA with values provided by the user.
    Request configuration steps from the user.
    """

    otp = data.get("otp")
    if otp is not None:
        otpPattern = "[0-9]{4}"
        m = re.match(otpPattern, otp)

        if m:
            return {
                "title": "otp",
                "otp": data.get("otp")
            }
        else:
            return None
    return None


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

            return self.async_create_entry(title=info["title"], data=info["data"])


        return self.async_show_form(
            step_id="user", data_schema=self._async_build_schema(), errors=errors
        )


    async def async_get_phone(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate user input
            valid = await is_phone_valid(user_input)
            if valid:
                # Store phone to use in next step
                self.phone = user_input["phone"]
                self.imei = send_otp_request(self.phone)

                # Return the form of the next step
                return await self.async_get_ota_token()
            
            errors["base"] = "invalid_phone"

        # Specify items in the order they are to be displayed in the UI
        data_schema = {
            vol.Required("phone"): str,
        }

        return self.async_show_form(
            step_id="get_phone", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def async_get_ota_token(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate user input
            valid = await is_otp_valid(user_input)
            if valid:
                # Store info to use in next step
                otp = user_input["otp"]
                self.token = get_otp_token(self.imei, self.phone, otp)

                # Return the form of the next step
                return await self.async_get_devices()

            errors["base"] = "invalid_token"

        # Specify items in the order they are to be displayed in the UI
        data_schema = {
            vol.Required("token"): str,
        }

        return self.async_show_form(
            step_id="get_phone", data_schema=vol.Schema(data_schema), errors=errors
        )

    async def get_devices(self):
        errors = {}

        devices = get_devices(self.imei, self.token)

        acs = []
        
        for device in devices:
            device_id = device['id']
            device_name = device['name']
            ac = { "id": device_id, "name": device_name }
            acs.append(ac)            

        self.acs = acs

        return self.async_create_entry(
            title="ElectraSmart",
            data={
                "imei": self.imei,
                "token": self.token,
                "acs": self.acs
            })
