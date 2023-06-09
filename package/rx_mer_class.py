# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2,
# as published by the Free Software Foundation.
#
# Project: OpenPNM
# Author: Maurice M. Garcia
# Contact: mgarcia01752@outlook.com
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from package.constants import *
from package.log import Log
from package.pnmHeader_class import PnmHeader
from typing import Union, List
import json


class RxMerDataValue:
    """
    Represents a single RxMER value for a subcarrier.
    """

    NO_MEASUREMENT: int = 0xFF
    MAX_REPORTED_VALUE: float = 63.5

    def __init__(self, value: Union[float, int]) -> None:
        """
        Initialize a RxMerDataValue.

        Args:
            value (float or int): RxMER value as a float or byte value.
        """
        self.value: float = self._validate_value(value)

    @staticmethod
    def _validate_value(value: Union[float, int]) -> float:
        """
        Validate and convert the RxMER value.

        Args:
            value (float or int): RxMER value as a float or byte value.

        Returns:
            float: Converted RxMER value.
        """
        if isinstance(value, int):
            if value == RxMerDataValue.NO_MEASUREMENT:
                return RxMerDataValue.NO_MEASUREMENT
            value = min(max(value, 0), int(RxMerDataValue.MAX_REPORTED_VALUE * 4))
            return value / 4.0

        if isinstance(value, float):
            value = min(max(value, 0.0), RxMerDataValue.MAX_REPORTED_VALUE)
            return value

        raise ValueError("Invalid RxMER value")

    def isMaxValue(self) -> bool:
        """
        Check if the RxMER value is the maximum reported value.

        Returns:
            bool: True if the RxMER value is the maximum reported value, False otherwise.
        """
        return self.value == RxMerDataValue.MAX_REPORTED_VALUE

    def getRxMER(self) -> float:
        """
        Get the RxMER value.

        Returns:
            float: The RxMER value.
        """
        return self.value

    def isMeasurement(self) -> bool:
        """
        Check if a measurement is available for the RxMER value.

        Returns:
            bool: True if a measurement is available, False otherwise.
        """
        return self.value != RxMerDataValue.NO_MEASUREMENT

    def toJson(self) -> str:
        """
        Convert the RxMerDataValue to a JSON string.

        Returns:
            str: JSON representation of the RxMerDataValue.
        """
        return json.dumps({
            "value": self.value,
            "isMaxValue": self.isMaxValue(),
            "isMeasurement": self.isMeasurement()
        })


class RxMerData:
    """
    Represents a sequence of received modulation error ratio (RxMER) values for a downstream OFDM channel.
    """

    def __init__(self, values: List[RxMerDataValue]) -> None:
        """
        Initialize RxMerData.

        Args:
            values (list): List of RxMerDataValues.
        """
        self.values: List[RxMerDataValue] = values
        Log.debug("Length of RxMer Data: " + str(self.size()))

    def size(self) -> int:
        return len(self.values)

    def toJson(self) -> str:
        """
        Convert the RxMerData to a JSON string.

        Returns:
            str: JSON representation of the RxMerData.
        """
        return json.dumps({
            "values": [value.toJson() for value in self.values]
        })


class RX_MER:
    def __init__(self, pnm_header: PnmHeader):
        """
        Initialize the RX_MER object.

        Args:
            pnm_header (PnmHeader): Instance of the PnmHeader class.
        """
        self.pnm_header = pnm_header
        self.rxmer_data = None

    def process_data(self):
        """
        Process the data received from PNM_HEADER.

        This method can be modified to perform the desired operations on the data.
        """
        Log.debug("Processing data from PNM_HEADER: " + str(self.pnm_header.getPnmData()))
        # Perform the desired operations on the data here
        self.rxmer_data = self._parse_rxmer_data()

    def _parse_rxmer_data(self) -> RxMerData:
        """
        Parse the PNM data and extract the RxMER values.

        Returns:
            RxMerData: The RxMER data.
        """
        pnm_data = self.pnm_header.getPnmData()
        if pnm_data is not None:
            # Convert BytesIO object to list of values
            pnm_data_list = list(pnm_data.getvalue())
            # Parse the pnm_data_list and extract the RxMER values
            values = [RxMerDataValue(value) for value in pnm_data_list]  # Modify parsing logic if needed
            return RxMerData(values)
        else:
            return RxMerData([])  # Return an empty RxMerData if PNM_DATA is not available


    def toJson(self) -> str:
        """
        Convert the RX_MER object to a JSON string.

        Returns:
            str: JSON representation of the RX_MER object.
        """
        return self.rxmer_data.toJson()

    def run(self):
        """
        Run the RX_MER processing.

        This method can be modified to fit the desired workflow.
        """
        self.process_data()
