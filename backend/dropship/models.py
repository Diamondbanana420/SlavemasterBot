"""Data models for dropshipping system"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Product Models
class Product(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    shopify_id: Optional[str] = None
    title: str
    sku: str
    price: float
    cost: float
    supplier_price: float = 0
    inventory_qty: int = 0
    supplier: Optional[str] = None
    supplier_sku: Optional[str] = None
    category: Optional[str] = None
    status: str = 'active'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def profit_margin(self) -> float:
        if self.price == 0:
            return 0
        return ((self.price - self.cost) / self.price) * 100

class Competitor(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    url: str
    products: List[Dict[str, Any]] = []
    last_checked: Optional[datetime] = None
    
class PriceHistory(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    product_id: str
    our_price: float
    competitor_price: Optional[float] = None
    competitor_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Analytics Models
class DailyMetrics(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    date: str
    revenue: float = 0
    orders: int = 0
    visitors: int = 0
    conversion_rate: float = 0
    avg_order_value: float = 0
    cart_abandonment_rate: float = 0
    profit: float = 0
    ad_spend: float = 0
    roas: float = 0  # Return on ad spend
    
class CustomerSegment(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    criteria: Dict[str, Any]
    customer_count: int = 0
    avg_ltv: float = 0
    
# Order Models
class Order(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    shopify_id: Optional[str] = None
    customer_email: str
    total: float
    items: List[Dict[str, Any]]
    status: str = 'pending'
    fulfillment_status: str = 'unfulfilled'
    supplier_order_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
# Alert Models
class Alert(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    type: str  # low_stock, price_change, conversion_drop, competitor_price
    severity: str = 'info'  # info, warning, critical
    title: str
    message: str
    data: Dict[str, Any] = {}
    acknowledged: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
