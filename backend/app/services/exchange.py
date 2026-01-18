"""
Exchange service for interacting with Buda.com and other exchanges.
Uses CCXT for standardized API access.
Includes simulation mode for paper trading without API keys.
"""

import random
import time
from decimal import Decimal
from typing import Optional

from loguru import logger

# Try to import ccxt, but don't fail if not available
try:
    import ccxt.async_support as ccxt
    CCXT_AVAILABLE = True
except ImportError:
    ccxt = None
    CCXT_AVAILABLE = False


class SimulatedExchange:
    """
    Simulated exchange for paper trading without API keys.
    Generates realistic-looking BTC-CLP price data.
    """

    def __init__(self):
        # Base price for BTC-CLP (approximately 90M CLP ~ $90k USD)
        self._base_price = 90_000_000
        self._volatility = 0.02  # 2% volatility
        self._last_price = self._base_price
        self._price_history: list[dict] = []
        self._initialize_history()

    def _initialize_history(self):
        """Generate initial price history."""
        now = int(time.time() * 1000)
        hour_ms = 3600 * 1000

        # Generate 100 hours of history
        price = self._base_price
        for i in range(100, 0, -1):
            timestamp = now - (i * hour_ms)

            # Random walk with mean reversion
            change = random.gauss(0, self._volatility * price)
            mean_reversion = (self._base_price - price) * 0.01
            price = max(price + change + mean_reversion, price * 0.9)

            # Generate OHLCV candle
            open_price = price
            high = price * (1 + random.uniform(0, 0.01))
            low = price * (1 - random.uniform(0, 0.01))
            close = price + random.gauss(0, price * 0.005)
            volume = random.uniform(0.5, 5.0)

            self._price_history.append({
                "timestamp": timestamp,
                "open": Decimal(str(round(open_price))),
                "high": Decimal(str(round(high))),
                "low": Decimal(str(round(low))),
                "close": Decimal(str(round(close))),
                "volume": Decimal(str(round(volume, 8))),
            })

            price = close

        self._last_price = float(price)

    def get_current_price(self) -> Decimal:
        """Get current simulated price with small random movement."""
        change = random.gauss(0, self._volatility * self._last_price * 0.1)
        mean_reversion = (self._base_price - self._last_price) * 0.001
        self._last_price = max(
            self._last_price + change + mean_reversion,
            self._last_price * 0.95
        )
        return Decimal(str(round(self._last_price)))

    def get_ohlcv(self, limit: int = 100) -> list[dict]:
        """Get simulated OHLCV data."""
        # Add a new candle if needed (every hour)
        now = int(time.time() * 1000)
        if self._price_history:
            last_timestamp = self._price_history[-1]["timestamp"]
            hour_ms = 3600 * 1000

            if now - last_timestamp >= hour_ms:
                price = self._last_price
                self._price_history.append({
                    "timestamp": now,
                    "open": Decimal(str(round(price))),
                    "high": Decimal(str(round(price * 1.005))),
                    "low": Decimal(str(round(price * 0.995))),
                    "close": self.get_current_price(),
                    "volume": Decimal(str(round(random.uniform(0.5, 5.0), 8))),
                })

        return self._price_history[-limit:]


class ExchangeService:
    """Service for exchange operations."""

    def __init__(
        self,
        exchange_id: str = "buda",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        simulation_mode: bool = False,
    ):
        self.exchange_id = exchange_id
        self.api_key = api_key
        self.api_secret = api_secret
        self._exchange = None
        self._simulated: Optional[SimulatedExchange] = None

        # Enable simulation mode if no API keys or explicitly requested
        self.simulation_mode = simulation_mode or not (api_key and api_secret)

        if self.simulation_mode:
            logger.info("Exchange service running in SIMULATION mode (no real API)")
            self._simulated = SimulatedExchange()

    async def _get_exchange(self):
        """Get or create exchange instance."""
        if self.simulation_mode:
            return None

        if self._exchange is None:
            if not CCXT_AVAILABLE:
                raise RuntimeError("CCXT not available and not in simulation mode")

            config = {
                "enableRateLimit": True,
            }

            if self.api_key and self.api_secret:
                config["apiKey"] = self.api_key
                config["secret"] = self.api_secret

            # Try to get the exchange class
            try:
                exchange_class = getattr(ccxt, self.exchange_id)
                self._exchange = exchange_class(config)
            except AttributeError:
                # Fallback to binance for data if buda not available
                logger.warning(f"Exchange '{self.exchange_id}' not found in CCXT, using binance")
                self._exchange = ccxt.binance(config)

        return self._exchange

    async def close(self):
        """Close exchange connection."""
        if self._exchange:
            await self._exchange.close()
            self._exchange = None

    async def get_balances(self) -> list[dict]:
        """Get all balances from exchange."""
        if self.simulation_mode:
            # Return empty balances for simulation
            return []

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
        if self.simulation_mode:
            price = self._simulated.get_current_price()
            return {
                "symbol": symbol,
                "last_price": price,
                "bid": price * Decimal("0.999"),
                "ask": price * Decimal("1.001"),
                "volume_24h": Decimal("10.5"),
                "change_24h_pct": random.uniform(-5, 5),
            }

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
        if self.simulation_mode:
            price = self._simulated.get_current_price()
            return [{
                "symbol": "BTC-CLP",
                "last_price": price,
                "bid": price * Decimal("0.999"),
                "ask": price * Decimal("1.001"),
                "volume_24h": Decimal("10.5"),
                "change_24h_pct": random.uniform(-5, 5),
            }]

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
        if self.simulation_mode:
            return self._simulated.get_ohlcv(limit=limit)

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
        if self.simulation_mode:
            # Simulation doesn't support real orders
            raise RuntimeError("Cannot create real orders in simulation mode")

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
        if self.simulation_mode:
            raise RuntimeError("Cannot cancel orders in simulation mode")

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
