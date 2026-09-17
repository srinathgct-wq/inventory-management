import random
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from mock_data import inventory_items, orders, demand_forecasts, backlog_items, spending_summary, monthly_spending, category_spending, recent_transactions, purchase_orders

app = FastAPI(title="Factory Inventory Management System")

# Quarter mapping for date filtering
QUARTER_MAP = {
    'Q1-2025': ['2025-01', '2025-02', '2025-03'],
    'Q2-2025': ['2025-04', '2025-05', '2025-06'],
    'Q3-2025': ['2025-07', '2025-08', '2025-09'],
    'Q4-2025': ['2025-10', '2025-11', '2025-12']
}

def filter_by_month(items: list, month: Optional[str]) -> list:
    """Filter items by month/quarter based on order_date field"""
    if not month or month == 'all':
        return items

    if month.startswith('Q'):
        # Handle quarters
        if month in QUARTER_MAP:
            months = QUARTER_MAP[month]
            return [item for item in items if any(m in item.get('order_date', '') for m in months)]
    else:
        # Direct month match
        return [item for item in items if month in item.get('order_date', '')]

    return items

def apply_filters(items: list, warehouse: Optional[str] = None, category: Optional[str] = None,
                 status: Optional[str] = None) -> list:
    """Apply common filters to a list of items"""
    filtered = items

    if warehouse and warehouse != 'all':
        filtered = [item for item in filtered if item.get('warehouse') == warehouse]

    if category and category != 'all':
        filtered = [item for item in filtered if item.get('category', '').lower() == category.lower()]

    if status and status != 'all':
        filtered = [item for item in filtered if item.get('status', '').lower() == status.lower()]

    return filtered

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class InventoryItem(BaseModel):
    id: str
    sku: str
    name: str
    category: str
    warehouse: str
    quantity_on_hand: int
    reorder_point: int
    unit_cost: float
    location: str
    last_updated: str

class Order(BaseModel):
    id: str
    order_number: str
    customer: str
    items: List[dict]
    status: str
    order_date: str
    expected_delivery: str
    total_value: float
    actual_delivery: Optional[str] = None
    warehouse: Optional[str] = None
    category: Optional[str] = None

class DemandForecast(BaseModel):
    id: str
    item_sku: str
    item_name: str
    current_demand: int
    forecasted_demand: int
    trend: str
    period: str

class BacklogItem(BaseModel):
    id: str
    order_id: str
    item_sku: str
    item_name: str
    quantity_needed: int
    quantity_available: int
    days_delayed: int
    priority: str
    has_purchase_order: Optional[bool] = False

class PurchaseOrder(BaseModel):
    id: str
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    status: str
    created_date: str
    notes: Optional[str] = None

class CreatePurchaseOrderRequest(BaseModel):
    backlog_item_id: str
    supplier_name: str
    quantity: int
    unit_cost: float
    expected_delivery_date: str
    notes: Optional[str] = None

class RestockRecommendationItem(BaseModel):
    sku: str
    item_name: str
    category: str
    warehouse: str
    current_stock: int
    reorder_point: int
    current_demand: int
    forecasted_demand: int
    trend: str
    unit_cost: float
    recommended_quantity: int
    line_total: float
    lead_time_days: int

class RestockRecommendationResponse(BaseModel):
    budget: float
    total_cost: float
    remaining_budget: float
    recommendations: List[RestockRecommendationItem]

class RestockOrderItemInput(BaseModel):
    sku: str
    item_name: str
    quantity: int
    unit_cost: float
    lead_time_days: int

class CreateRestockOrderRequest(BaseModel):
    budget: float
    items: List[RestockOrderItemInput]

class RestockOrderItem(BaseModel):
    sku: str
    item_name: str
    quantity: int
    unit_cost: float
    line_total: float
    lead_time_days: int

class RestockOrder(BaseModel):
    id: str
    order_number: str
    budget: float
    total_cost: float
    item_count: int
    items: List[RestockOrderItem]
    lead_time_days: int
    status: str
    created_date: str
    expected_delivery: str

# In-memory store for submitted restocking orders (resets on server restart)
restock_orders: List[dict] = []

def calculate_restock_recommendations(budget: float):
    """Rank inventory/demand pairs by urgency (increasing trend + largest demand/stock gap),
    then greedily fill the budget from the top of that ranking."""
    inventory_by_sku = {item['sku']: item for item in inventory_items}
    trend_weight = {'increasing': 2, 'stable': 1, 'decreasing': 0}

    candidates = []
    for forecast in demand_forecasts:
        inv = inventory_by_sku.get(forecast['item_sku'])
        if not inv or inv['unit_cost'] <= 0:
            continue

        demand_gap = max(forecast['forecasted_demand'] - forecast['current_demand'], 0)
        stock_gap = max(inv['reorder_point'] - inv['quantity_on_hand'], 0)
        needed_quantity = demand_gap + stock_gap
        if needed_quantity <= 0:
            continue

        # Trend dominates the ranking; gap size only breaks ties within a trend tier
        priority_score = trend_weight.get(forecast['trend'], 1) * 100000 + needed_quantity

        candidates.append({
            'sku': forecast['item_sku'],
            'item_name': forecast['item_name'],
            'category': inv['category'],
            'warehouse': inv['warehouse'],
            'current_stock': inv['quantity_on_hand'],
            'reorder_point': inv['reorder_point'],
            'current_demand': forecast['current_demand'],
            'forecasted_demand': forecast['forecasted_demand'],
            'trend': forecast['trend'],
            'unit_cost': inv['unit_cost'],
            'needed_quantity': needed_quantity,
            'priority_score': priority_score
        })

    candidates.sort(key=lambda c: c['priority_score'], reverse=True)

    recommendations = []
    remaining_budget = round(budget, 2)
    for c in candidates:
        if remaining_budget < c['unit_cost']:
            continue
        max_affordable = int(remaining_budget // c['unit_cost'])
        quantity = min(c['needed_quantity'], max_affordable)
        if quantity <= 0:
            continue

        line_total = round(quantity * c['unit_cost'], 2)
        remaining_budget = round(remaining_budget - line_total, 2)

        recommendations.append({
            'sku': c['sku'],
            'item_name': c['item_name'],
            'category': c['category'],
            'warehouse': c['warehouse'],
            'current_stock': c['current_stock'],
            'reorder_point': c['reorder_point'],
            'current_demand': c['current_demand'],
            'forecasted_demand': c['forecasted_demand'],
            'trend': c['trend'],
            'unit_cost': c['unit_cost'],
            'recommended_quantity': quantity,
            'line_total': line_total,
            'lead_time_days': random.randint(7, 21)
        })

    total_cost = round(budget - remaining_budget, 2)
    return recommendations, total_cost, remaining_budget

# API endpoints
@app.get("/")
def root():
    return {"message": "Factory Inventory Management System API", "version": "1.0.0"}

@app.get("/api/inventory", response_model=List[InventoryItem])
def get_inventory(
    warehouse: Optional[str] = None,
    category: Optional[str] = None
):
    """Get all inventory items with optional filtering"""
    return apply_filters(inventory_items, warehouse, category)

@app.get("/api/inventory/{item_id}", response_model=InventoryItem)
def get_inventory_item(item_id: str):
    """Get a specific inventory item"""
    item = next((item for item in inventory_items if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/api/orders", response_model=List[Order])
def get_orders(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get all orders with optional filtering"""
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)
    return filtered_orders

@app.get("/api/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    """Get a specific order"""
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/demand", response_model=List[DemandForecast])
def get_demand_forecasts():
    """Get demand forecasts"""
    return demand_forecasts

@app.get("/api/backlog", response_model=List[BacklogItem])
def get_backlog():
    """Get backlog items with purchase order status"""
    # Add has_purchase_order flag to each backlog item
    result = []
    for item in backlog_items:
        item_dict = dict(item)
        # Check if this backlog item has a purchase order
        has_po = any(po["backlog_item_id"] == item["id"] for po in purchase_orders)
        item_dict["has_purchase_order"] = has_po
        result.append(item_dict)
    return result

@app.get("/api/restock/recommendations", response_model=RestockRecommendationResponse)
def get_restock_recommendations(budget: float):
    """Recommend items to restock within a given budget, prioritizing rising demand
    and items that have fallen below their reorder point."""
    if budget <= 0:
        return {"budget": budget, "total_cost": 0, "remaining_budget": budget, "recommendations": []}

    recommendations, total_cost, remaining_budget = calculate_restock_recommendations(budget)
    return {
        "budget": budget,
        "total_cost": total_cost,
        "remaining_budget": remaining_budget,
        "recommendations": recommendations
    }

@app.get("/api/restock-orders", response_model=List[RestockOrder])
def get_restock_orders():
    """Get all submitted restocking orders"""
    return restock_orders

@app.post("/api/restock-orders", response_model=RestockOrder)
def create_restock_order(request: CreateRestockOrderRequest):
    """Submit a restocking order built from recommended items"""
    if not request.items:
        raise HTTPException(status_code=400, detail="Restock order must include at least one item")

    order_items = []
    total_cost = 0.0
    max_lead_time = 0
    for item in request.items:
        line_total = round(item.quantity * item.unit_cost, 2)
        total_cost += line_total
        max_lead_time = max(max_lead_time, item.lead_time_days)
        order_items.append({
            "sku": item.sku,
            "item_name": item.item_name,
            "quantity": item.quantity,
            "unit_cost": item.unit_cost,
            "line_total": line_total,
            "lead_time_days": item.lead_time_days
        })

    created_date = datetime.now()
    # Order-level lead time is the slowest item, since that's what determines when the order is fully complete
    expected_delivery = created_date + timedelta(days=max_lead_time)

    order = {
        "id": str(len(restock_orders) + 1),
        "order_number": f"RSK-{len(restock_orders) + 1:04d}",
        "budget": request.budget,
        "total_cost": round(total_cost, 2),
        "item_count": len(order_items),
        "items": order_items,
        "lead_time_days": max_lead_time,
        "status": "Processing",
        "created_date": created_date.isoformat(),
        "expected_delivery": expected_delivery.isoformat()
    }
    restock_orders.append(order)
    return order

@app.get("/api/dashboard/summary")
def get_dashboard_summary(
    warehouse: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[str] = None
):
    """Get summary statistics for dashboard with optional filtering"""
    # Filter inventory
    filtered_inventory = apply_filters(inventory_items, warehouse, category)

    # Filter orders
    filtered_orders = apply_filters(orders, warehouse, category, status)
    filtered_orders = filter_by_month(filtered_orders, month)

    total_inventory_value = sum(item["quantity_on_hand"] * item["unit_cost"] for item in filtered_inventory)
    low_stock_items = len([item for item in filtered_inventory if item["quantity_on_hand"] <= item["reorder_point"]])
    pending_orders = len([order for order in filtered_orders if order["status"] in ["Processing", "Backordered"]])
    total_backlog_items = len(backlog_items)

    return {
        "total_inventory_value": round(total_inventory_value, 2),
        "low_stock_items": low_stock_items,
        "pending_orders": pending_orders,
        "total_backlog_items": total_backlog_items,
        "total_orders_value": sum(order["total_value"] for order in filtered_orders)
    }

@app.get("/api/spending/summary")
def get_spending_summary():
    """Get spending summary statistics"""
    return spending_summary

@app.get("/api/spending/monthly")
def get_monthly_spending():
    """Get monthly spending breakdown"""
    return monthly_spending

@app.get("/api/spending/categories")
def get_category_spending():
    """Get spending by category"""
    return category_spending

@app.get("/api/spending/transactions")
def get_recent_transactions():
    """Get recent transactions"""
    return recent_transactions

@app.get("/api/reports/quarterly")
def get_quarterly_reports():
    """Get quarterly performance reports"""
    # Calculate quarterly statistics from orders
    quarters = {}

    for order in orders:
        order_date = order.get('order_date', '')
        # Determine quarter
        if '2025-01' in order_date or '2025-02' in order_date or '2025-03' in order_date:
            quarter = 'Q1-2025'
        elif '2025-04' in order_date or '2025-05' in order_date or '2025-06' in order_date:
            quarter = 'Q2-2025'
        elif '2025-07' in order_date or '2025-08' in order_date or '2025-09' in order_date:
            quarter = 'Q3-2025'
        elif '2025-10' in order_date or '2025-11' in order_date or '2025-12' in order_date:
            quarter = 'Q4-2025'
        else:
            continue

        if quarter not in quarters:
            quarters[quarter] = {
                'quarter': quarter,
                'total_orders': 0,
                'total_revenue': 0,
                'delivered_orders': 0,
                'avg_order_value': 0
            }

        quarters[quarter]['total_orders'] += 1
        quarters[quarter]['total_revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            quarters[quarter]['delivered_orders'] += 1

    # Calculate averages and fulfillment rate
    result = []
    for q, data in quarters.items():
        if data['total_orders'] > 0:
            data['avg_order_value'] = round(data['total_revenue'] / data['total_orders'], 2)
            data['fulfillment_rate'] = round((data['delivered_orders'] / data['total_orders']) * 100, 1)
        result.append(data)

    # Sort by quarter
    result.sort(key=lambda x: x['quarter'])
    return result

@app.get("/api/reports/monthly-trends")
def get_monthly_trends():
    """Get month-over-month trends"""
    months = {}

    for order in orders:
        order_date = order.get('order_date', '')
        if not order_date:
            continue

        # Extract month (format: YYYY-MM-DD)
        month = order_date[:7]  # Gets YYYY-MM

        if month not in months:
            months[month] = {
                'month': month,
                'order_count': 0,
                'revenue': 0,
                'delivered_count': 0
            }

        months[month]['order_count'] += 1
        months[month]['revenue'] += order.get('total_value', 0)
        if order.get('status') == 'Delivered':
            months[month]['delivered_count'] += 1

    # Convert to list and sort
    result = list(months.values())
    result.sort(key=lambda x: x['month'])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
