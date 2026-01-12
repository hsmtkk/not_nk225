import dataclasses
import logging
import os
import time

import pandas
import yfinance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        price=int(info["currentPrice"]),
        volume=int(info["volume"]),
        marketCapacity=int(info.get("marketCap", 0)),
        pbr=info.get("priceToBook", 0),
        per=info.get("trailingPE", 0),
    )


def add_stock_info(stock_data: pandas.DataFrame) -> pandas.DataFrame:
    stock_info_list = []
    for _, row in stock_data.iterrows():
        logger.info(f"processing {row['コード']} {row['銘柄名']}")
        code = row["コード"]
        stock_info = get_stock_info(code)
        stock_info_list.append(dataclasses.asdict(stock_info))
        time.sleep(0.1)
    stock_info_df = pandas.DataFrame(stock_info_list)
    return pandas.merge(stock_data, stock_info_df, left_on="コード", right_on="code")


def save_result(stock_data: pandas.DataFrame, file_path: str | os.PathLike) -> None:
    output_fields = [
        "コード",
        "銘柄名",
        "price",
        "volume",
        "marketCapacity",
        "pbr",
        "per",
    ]
    stock_data[output_fields].to_csv(file_path, index=False)


def main():
    prime_stocks = get_prime_stocks()
    nk225_stocks = get_nikkei_225_stocks()
    result = select_not_nk225_stocks(prime_stocks, nk225_stocks)
    result_with_info = add_stock_info(result)
    save_result(result_with_info, "./output/prime_not_nk225.csv")


if __name__ == "__main__":
    main()
