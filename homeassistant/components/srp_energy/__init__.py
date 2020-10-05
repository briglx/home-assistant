"""The SRP Energy integration."""
import logging

from srpenergy.client import SrpEnergyClient
import voluptuous as vol

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_ID, CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv

from .const import DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_ID): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up SRP Energy from a config entry."""
    if DOMAIN in config:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data=config[DOMAIN]
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the SRP Energy component.

    Called after setup.
    """
    account_id = entry.data.get(CONF_ID)
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)

    try:

        srp_energy_client = await hass.async_add_executor_job(
            SrpEnergyClient, account_id, username, password
        )
        hass.data[DOMAIN] = srp_energy_client
    except (Exception) as ex:
        _LOGGER.error("Unable to connect to Srp Energy: %s", str(ex))
        raise ConfigEntryNotReady from ex

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""

    # unload_ok = all(
    #     await asyncio.gather(
    #         *[
    #             hass.config_entries.async_forward_entry_unload(entry, component)
    #             for component in PLATFORMS
    #         ]
    #     )
    # )

    # unload srp client
    hass.data[DOMAIN] = None

    # Remove config entry
    await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")

    hass.data.pop(DOMAIN)

    return True