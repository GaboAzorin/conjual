"""
Exchange service for interacting with Buda.com and other exchanges.
Uses CCXT for standardized API access.
"""

from decimal import Decimal
from typing import Optional

import ccxt.async_support as ccxt
from loguru import logger


class ExchangeService:
    """Service for exchange operations."""

    def __init__(
        self,
        exchange_id: str = "buda",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ):
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.api_secret = api_secret
        self._exchange = None

    async def _get_exchange(self) -> ccxt.Exchange:
        """Get or create exchange instance."""
        if self._exchange is None:
            config = {
                "enableRateLimit": True,
            }

            if self.api_key and self.api_secret:
                config["apiKey"] = self.api_key
                config["secret"] = self.api_secret

            # CCXT uses 'buda' as the exchange id
            exchange_class = getattr(ccxt, self.exchange_id)
            self._exchange = exchange_class(config)

        return self._exchange

    async def close(self):
        """Close exchange connection."""
        if self._exchange:
            await self._exchange.close()
            self._exchange = None

    async def get_balances(self) -> list[dict]:
        """Get all balances from exchange."""
        exchange = await self._get_exchange()

        try:
            balance = await exchange.fetch_balance()

            balances = []
            for currency, data in balance.get("total", {}).items():
                if data and data > 0:
                    balances.append({
                        "currency": currency,
                        "available": Decimal(str(balance["free"].get(currency, 0))),
                        "frozen": Decimal(str(balance["used"].get(currency, 0))),
                        "total": Decimal(str(data)),
                    })

            return balances

        except Exception as e:
            logger.error(f"Error fetching balances: {e}")
            raise

    async def get_ticker(self, symbol: str) -> dict:
        """Get ticker for a symbol."""
        exchange = await self._get_exchange()

        # Convert symbol format (BTC-CLP -> BTC/CLP)
        ccxt_symbol = symbol.replace("-", "/")

        try:
            ticker = await exchange.fetch_ticker(ccxt_symbol)

            return {
                "symbol": symbol,
                "last_price": Decimal(str(ticker["last"])) if ticker["last"] else Decimal(0),
                "bid": Decimal(str(ticker["bid"])) if ticker["bid"] else Decimal(0),
                "ask": Decimal(str(ticker["ask"])) if ticker["ask"] else Decimal(0),
                "volume_24h": Decimal(str(ticker["baseVolume"])) if ticker["baseVolume"] else Decimal(0),
                "change_24h_pct": ticker.get("percentage", 0) or 0,
            }

        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise

    async def get_all_tickers(self) -> list[dict]:
        """Get tickers for all markets."""
        exchange = await self._get_exchange()

        try:
            tickers = await exchange.fetch_tickers()

            result = []
            for symbol, ticker in tickers.items():
                result.append({
                    "symbol": symbol.replace("/", "-"),
                    "last_price": Decimal(str(ticker["last"])) if ticker["last"] else Decimal(0),
                    "bid": Decimal(str(ticker["bid"])) if ticker["bid"] else Decimal(0),
                    "ask": Decimal(str(ticker["ask"])) if ticker["ask"] else Decimal(0),
                    "volume_24h": Decimal(str(ticker["baseVolume"])) if ticker["baseVolume"] else Decimal(0),
                    "change_24h_pct": ticker.get("percentage", 0) or 0,
                })

            return result

        except Exception as e:
            logger.error(f"Error fetching all tickers: {e}")
            raise

    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100,
        since: Optional[int] = None,
    ) -> list[dict]:
        """Get OHLCV candlestick data."""
        exchange = await self._get_exchange()
        ccxt_symbol = symbol.replace("-", "/")

        try:
            ohlcv = await exchange.fetch_ohlcv(
                ccxt_symbol,
                timeframe,
                since=since,
                limit=limit,
            )

            return [
                {
                    "timestamp": candle[0],
                    "open": Decimal(str(candle[1])),
                    "high": Decimal(str(candle[2])),
                    "low": Decimal(str(candle[3])),
                    "close": Decimal(str(candle[4])),
                    "volume": Decimal(str(candle[5])),
                }
                for candle in ohlcv
            ]

        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            raise

    async def create_order(
        self,
        symbol: str,
        side: str,  # "buy" or "sell"
        order_type: str,  # "market" or "limit"
        amount: Decimal,
        price: Optional[Decimal] = None,
    ) -> dict:
        """Create a new order."""
        exchange = await self._get_exchange()
        ccxt_symbol = symbol.replace("-", "/")

        try:
            if order_type == "market":
                order = await exchange.create_market_order(
                    ccxt_symbol,
                    side,
                    float(amount),
                )
            else:
                if price is None:
                    raise ValueError("Price is required for limit orders")

                order = await exchange.create_limit_order(
                    ccxt_symbol,
                    side,
                    float(amount),
                    float(price),
                )

            logger.info(f"Order created: {order['id']} - {side} {amount} {symbol}")

            return {
                "id": order["id"],
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "amount": Decimal(str(order["amount"])),
                "price": Decimal(str(order["price"])) if order["price"] else None,
                "status": order["status"],
            }

        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order."""
        exchange = await self._get_exchange()
        ccxt_symbol = symbol.replace("-", "/")

        try:
            await exchange.cancel_order(order_id, ccxt_symbol)
            logger.info(f"Order cancelled: {order_id}")
            return True

        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            raise

    async def calculate_total_value_clp(self, balances: list[dict]) -> Decimal:
        """Calculate total portfolio value in CLP."""
        total = Decimal(0)

        for balance in balances:
            currency = balance["currency"]
            amount = balance["total"]

            if currency == "CLP":
                total += amount
            elif amount > 0:
                try:
                    ticker = await self.get_ticker(f"{currency}-CLP")
                    total += amount * ticker["last_price"]
                except Exception:
                    # Skip if we can't get price
                    pass

        return total
