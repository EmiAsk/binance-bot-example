import time
from pprint import pprint
from threading import Thread

from binance_client import get_candlesticks, get_exchange_information
from config import INTERVAL_MS, MS_2_SEC, COUNT_CANDLESTICKS, INTERVAL, OPEN_PRICE_INDEX, TRIGGER_PERCENT, \
    CLOSE_PRICE_INDEX, DELAY_MS
from tg_client import queue, start_client


def send_message(msg: str):
    queue.put(msg)


def get_perp_pairs_by_margin_asset(symbols: list[dict], margin_asset: str) -> list[str]:
    cond = lambda symbol: symbol["contractType"] == "PERPETUAL" and symbol["marginAsset"] == margin_asset.upper()
    return list(map(lambda symbol: symbol["pair"], filter(cond, symbols)))


def get_percent_diff(before: float, after: float) -> float:
    return after / before - 1 if (after >= before) else -(1 - (after / before))


def calculate_candle_start(now_ms: int, diff: int) -> int:
    return (now_ms // INTERVAL_MS + diff) * INTERVAL_MS


def start_watching(pair: str):
    while True:
        now_ms = int(time.time() * MS_2_SEC)
        next_candle_start = calculate_candle_start(now_ms, 1)

        time.sleep((next_candle_start - now_ms) / MS_2_SEC + DELAY_MS / MS_2_SEC)  # delay used to see new candle

        candles = get_candlesticks(pair, COUNT_CANDLESTICKS + 1, INTERVAL)
        n_candles_back = candles[0]
        current_candle = candles[-1]

        percent_diff = get_percent_diff(float(n_candles_back[OPEN_PRICE_INDEX]),
                                        float(current_candle[CLOSE_PRICE_INDEX]))

        if abs(percent_diff) >= TRIGGER_PERCENT / 100:
            msg = f"{pair}\nPercent: {percent_diff * 100}\nInterval: {INTERVAL}\nCount klines: {COUNT_CANDLESTICKS}"
            send_message(msg)


def main():
    exchange_info = get_exchange_information()["symbols"]
    pairs = get_perp_pairs_by_margin_asset(exchange_info, "USDC")
    pprint(pairs)
    threads = []

    for pair in pairs:
        th = Thread(target=start_watching, args=(pair,), daemon=True)
        th.start()
        threads.append(th)

    start_client()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
