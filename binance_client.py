from typing import Optional, Union

from requests import get

from config import REST_API_ENDPOINT


def get_exchange_information():
    response = get(REST_API_ENDPOINT + "/fapi/v1/exchangeInfo")
    if response:
        return response.json()


def get_candlesticks(
        pair: str,
        limit: int,
        interval: str,
        start_time: int = None
) -> Optional[list[list[Union[str, int]]]]:
    response = get(
        REST_API_ENDPOINT + "/fapi/v1/continuousKlines",
        params={
            "pair": pair.lower(),
            "contractType": "PERPETUAL",
            "limit": limit,
            "interval": interval,
            "startTime": start_time
        }
    )
    if response:
        return response.json()
