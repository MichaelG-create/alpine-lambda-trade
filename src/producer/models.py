from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class Trade(BaseModel):
    model_config = ConfigDict(strict=False)

    id: str
    symbol: str
    price: float
    amount: float
    cost: float
    side: str
    timestamp: int
    datetime: datetime

    def to_dict(self) -> dict:
        return self.model_dump()
