"""Contact Energy API."""

import logging
import requests

_LOGGER = logging.getLogger(__name__)


class ContactEnergyApi:
    """Class for Contact Energy API."""

    def __init__(self, email, password):
        """Initialise Contact Energy API."""
        self._api_token = ""
        self._contractId = ""
        self._accountId = ""
        self._url_base = "https://api.contact-digital-prod.net"
        self._api_key = "z840P4lQCH9TqcjC9L2pP157DZcZJMcr5tVQCvyx"
        self._email = email
        self._password = password

    def login(self):
        """Login to the Contact Energy API."""
        headers = {"x-api-key": self._api_key}
        data = {"username": self._email, "password": self._password}
        result = requests.post(self._url_base + "/login/v2", json=data, headers=headers)
        if result.status_code == requests.codes.ok:
            jsonResult = result.json()
            self._api_token = jsonResult["token"]
            _LOGGER.debug("Logged in")
            return self.get_accounts()
        else:
            _LOGGER.error(
                "Failed to login - check the username and password are valid",
                result.text,
            )
            return False

    def get_accounts(self):
        """Get the first electricity account that we see."""
        headers = {"x-api-key": self._api_key, "session": self._api_token}
        result = requests.get(self._url_base + "/accounts/v2", headers=headers)
        if result.status_code == requests.codes.ok:
            _LOGGER.debug("Retrieved accounts")
            data = result.json()
            self._accountId = data["accountDetail"]["id"]
            contracts = data["accountDetail"]["contracts"]
            electricityContracts = [
                contract
                for contract in contracts
                if contract["contractType"] == 1  # "contractTypeLabel": "Electricity"
            ]
            self._contractId = electricityContracts[0]["id"]
            return True
        else:
            _LOGGER.error("Failed to fetch customer accounts %s", result.text)
            return False

    def get_usage(self, year, month, day):
        """Update our usage data."""
        headers = {"x-api-key": self._api_key, "authorization": self._api_token}
        response = requests.post(
            self._url_base
            + "/usage/v2/"
            + self._contractId
            + "?ba="
            + self._accountId
            + "&interval=hourly&from="
            + year
            + "-"
            + (month.zfill(2))
            + "-"
            + (day.zfill(2))
            + "&to="
            + year
            + "-"
            + (month.zfill(2))
            + "-"
            + (day.zfill(2)),
            headers=headers,
        )
        data = {}
        if response.status_code == requests.codes.ok:
            data = response.json()
            if not data:
                _LOGGER.info(
                    "Fetched usage data for %s/%s/%s, but got nothing back",
                    year,
                    month,
                    day,
                )
            return data
        else:
            _LOGGER.error("Failed to fetch usage data for %s/%s/%s", year, month, day)
            _LOGGER.debug(response)
            return False
