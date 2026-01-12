import dataclasses

import pandas
import yfinance


def get_prime_stocks() -> pandas.DataFrame:
    tosyo_df = pandas.read_excel("./input/data_j.xls", dtype=str)
    prime_df = tosyo_df[tosyo_df["市場・商品区分"] == "プライム（内国株式）"]
    result = prime_df[["コード", "銘柄名"]]
    return result


def get_nikkei_225_stocks() -> pandas.DataFrame:
    nikkei_df = pandas.read_csv(
        "./input/nikkei_225_price_adjustment_factor_jp.csv",
        encoding="shift_jis",
        dtype=str,
    )
    result = nikkei_df[["コード", "銘柄名"]]
    return result


def select_not_nk225_stocks(
    prime_stocks: pandas.DataFrame, nk225_stocks: pandas.DataFrame
) -> pandas.DataFrame:
    not_nk225_stocks = prime_stocks[
        ~prime_stocks["コード"].isin(nk225_stocks["コード"])
    ]
    return not_nk225_stocks


@dataclasses.dataclass
class StockInfo:
    code: str
    shortName: str
    longName: str
    price: int  # 株価
    volume: int  # 出来高
    marketCapacity: int  # 時価総額
    pbr: float  # PBR
    per: float  # PER


def get_stock_info(code: str) -> StockInfo:
    ticker = yfinance.Ticker(f"{code}.T")
    info = ticker.info
    return StockInfo(
        code=code,
        shortName=info["shortName"],
        longName=info["longName"],
        price=int(info["currentPrice"]),
        volume=int(info["volume"]),
        marketCapacity=int(info["marketCap"]),
        pbr=info["priceToBook"],
        per=info["trailingPE"],
    )


if __name__ == "__main__":
    # prime_stocks = get_prime_stocks()
    # nk225_stocks = get_nikkei_225_stocks()
    # result = select_not_nk225_stocks(prime_stocks, nk225_stocks)
    # print(result)
    print(get_stock_info("1301"))
