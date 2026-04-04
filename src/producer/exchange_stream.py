import ccxt.pro as ccxt
import asyncio
import logging
from typing import List, Callable, Awaitable
from src.producer.config import settings

logger = logging.getLogger(__name__)

class ExchangeStream:
    def __init__(self, callbacks: List[Callable[[dict], Awaitable[None]]]):
        self.callbacks = callbacks
        self.exchange = getattr(ccxt, settings.exchange_id)()
        self.symbols = settings.symbol_list
        self.running = False

    async def start(self):
        self.running = True
        logger.info(f"Starting connection to {settings.exchange_id} for {self.symbols}...")
        
        while self.running:
            try:
                tasks = [self._watch_symbol(sym) for sym in self.symbols]
                await asyncio.gather(*tasks)
            except Exception as e:
                logger.error(f"Error in stream: {e}. Reconnecting...")
                if self.running:
                    await asyncio.sleep(5)
                
    async def _watch_symbol(self, symbol: str):
        while self.running:
            try:
                trades = await self.exchange.watch_trades(symbol)
                for trade in trades:
                    for callback in self.callbacks:
                        await callback(trade)
            except Exception as e:
                logger.error(f"Error watching {symbol}: {e}")
                raise e

    async def stop(self):
        self.running = False
        await self.exchange.close()
        logger.info(f"Exchange connection closed.")
