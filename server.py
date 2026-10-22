import json
import os
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from pydantic import Field

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "guru.json"
_db: dict = json.loads(_DATA_PATH.read_text())


def _match(record: dict, field: str, value: str) -> bool:
    """Case-insensitive substring match on a field."""
    return value.lower() in str(record.get(field, "")).lower()


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="guru-mock",
    version="1.0.0",
    instructions=(
        "Mock Guru knowledge base for PeakVital, a U.S.-based premium bovine colostrum "
        "wellness brand. Query knowledge-base articles, product catalog, customers, "
        "orders, reviews, and support tickets."
    ),
)

# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------

@mcp.tool()
def get_articles(
    article_id: Optional[str] = Field(default=None, description="Filter by article ID, e.g. ART001"),
    category: Optional[str] = Field(default=None, description="Filter by category (partial match), e.g. Science & Ingredients"),
    tag: Optional[str] = Field(default=None, description="Filter by tag (partial match), e.g. immune"),
    author: Optional[str] = Field(default=None, description="Filter by author name (partial match), e.g. Dr. Nair"),
    status: Optional[str] = Field(default=None, description="Filter by status: published | draft"),
    keyword: Optional[str] = Field(default=None, description="Full-text keyword search across title, summary, and content"),
) -> list[dict]:
    """List knowledge-base articles. Optionally filter by ID, category, tag, author, status, or keyword."""
    results = _db["articles"]
    if article_id:
        results = [r for r in results if r["article_id"].upper() == article_id.upper()]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    if tag:
        results = [r for r in results if any(tag.lower() in t.lower() for t in r.get("tags", []))]
    if author:
        results = [r for r in results if _match(r, "author", author)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if keyword:
        kw = keyword.lower()
        results = [
            r for r in results
            if kw in r.get("title", "").lower()
            or kw in r.get("summary", "").lower()
            or kw in r.get("content", "").lower()
        ]
    return results


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

@mcp.tool()
def get_products(
    product_id: Optional[str] = Field(default=None, description="Filter by product ID, e.g. PROD001"),
    sku: Optional[str] = Field(default=None, description="Filter by SKU, e.g. PV-CP-100"),
    category: Optional[str] = Field(default=None, description="Filter by category (partial match), e.g. Core Supplement"),
    form: Optional[str] = Field(default=None, description="Filter by form: powder | capsule | stick_pack | bundle"),
    in_stock: Optional[bool] = Field(default=None, description="Filter by in-stock status: true or false"),
    certification: Optional[str] = Field(default=None, description="Filter by certification (partial match), e.g. NSF Sport"),
) -> list[dict]:
    """List products. Optionally filter by ID, SKU, category, form, in-stock status, or certification."""
    results = _db["products"]
    if product_id:
        results = [r for r in results if r["product_id"].upper() == product_id.upper()]
    if sku:
        results = [r for r in results if r["sku"].upper() == sku.upper()]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    if form:
        results = [r for r in results if _match(r, "form", form)]
    if in_stock is not None:
        results = [r for r in results if r.get("in_stock") == in_stock]
    if certification:
        results = [
            r for r in results
            if any(certification.lower() in c.lower() for c in r.get("certifications", []))
        ]
    return results


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@mcp.tool()
def get_customers(
    customer_id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. CUS001"),
    last_name: Optional[str] = Field(default=None, description="Filter by last name (partial match)"),
    email: Optional[str] = Field(default=None, description="Filter by email (partial match)"),
    segment: Optional[str] = Field(default=None, description="Filter by segment: athlete | wellness_general | biohacker | gut_health | beauty"),
    loyalty_tier: Optional[str] = Field(default=None, description="Filter by loyalty tier: bronze | silver | gold | platinum"),
    subscription_active: Optional[bool] = Field(default=None, description="Filter by active subscription status: true or false"),
) -> list[dict]:
    """List customers. Optionally filter by ID, name, email, segment, loyalty tier, or subscription status."""
    results = _db["customers"]
    if customer_id:
        results = [r for r in results if r["customer_id"].upper() == customer_id.upper()]
    if last_name:
        results = [r for r in results if _match(r, "last_name", last_name)]
    if email:
        results = [r for r in results if _match(r, "email", email)]
    if segment:
        results = [r for r in results if _match(r, "segment", segment)]
    if loyalty_tier:
        results = [r for r in results if _match(r, "loyalty_tier", loyalty_tier)]
    if subscription_active is not None:
        results = [r for r in results if r.get("subscription_active") == subscription_active]
    return results


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

@mcp.tool()
def get_orders(
    order_id: Optional[str] = Field(default=None, description="Filter by order ID, e.g. ORD10001"),
    customer_id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. CUS001"),
    status: Optional[str] = Field(default=None, description="Filter by order status: processing | shipped | delivered | cancelled"),
    sku: Optional[str] = Field(default=None, description="Filter orders containing a specific SKU, e.g. PV-CP-100"),
    subscription_order: Optional[bool] = Field(default=None, description="Filter by subscription order: true or false"),
) -> list[dict]:
    """List orders. Optionally filter by order ID, customer, status, SKU, or subscription flag."""
    results = _db["orders"]
    if order_id:
        results = [r for r in results if r["order_id"].upper() == order_id.upper()]
    if customer_id:
        results = [r for r in results if r["customer_id"].upper() == customer_id.upper()]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if sku:
        results = [
            r for r in results
            if any(sku.upper() == item["sku"].upper() for item in r.get("items", []))
        ]
    if subscription_order is not None:
        results = [r for r in results if r.get("subscription_order") == subscription_order]
    return results


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

@mcp.tool()
def get_reviews(
    review_id: Optional[str] = Field(default=None, description="Filter by review ID, e.g. REV001"),
    customer_id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. CUS001"),
    product_sku: Optional[str] = Field(default=None, description="Filter by product SKU, e.g. PV-CP-100"),
    min_rating: Optional[int] = Field(default=None, description="Filter by minimum star rating (1-5)"),
    keyword: Optional[str] = Field(default=None, description="Keyword search across headline and body text"),
) -> list[dict]:
    """List product reviews. Optionally filter by review ID, customer, SKU, minimum rating, or keyword."""
    results = _db["reviews"]
    if review_id:
        results = [r for r in results if r["review_id"].upper() == review_id.upper()]
    if customer_id:
        results = [r for r in results if r["customer_id"].upper() == customer_id.upper()]
    if product_sku:
        results = [r for r in results if r["product_sku"].upper() == product_sku.upper()]
    if min_rating is not None:
        results = [r for r in results if r.get("rating", 0) >= min_rating]
    if keyword:
        kw = keyword.lower()
        results = [
            r for r in results
            if kw in r.get("headline", "").lower() or kw in r.get("body", "").lower()
        ]
    return results


# ---------------------------------------------------------------------------
# Support Tickets
# ---------------------------------------------------------------------------

@mcp.tool()
def get_support_tickets(
    ticket_id: Optional[str] = Field(default=None, description="Filter by ticket ID, e.g. TKT001"),
    customer_id: Optional[str] = Field(default=None, description="Filter by customer ID, e.g. CUS001"),
    category: Optional[str] = Field(default=None, description="Filter by category: product_question | shipping | wholesale | billing | returns"),
    status: Optional[str] = Field(default=None, description="Filter by status: open | in_progress | resolved"),
    priority: Optional[str] = Field(default=None, description="Filter by priority: normal | high | urgent"),
    channel: Optional[str] = Field(default=None, description="Filter by channel: email | chat | phone"),
) -> list[dict]:
    """List support tickets. Optionally filter by ticket ID, customer, category, status, priority, or channel."""
    results = _db["support_tickets"]
    if ticket_id:
        results = [r for r in results if r["ticket_id"].upper() == ticket_id.upper()]
    if customer_id:
        results = [r for r in results if r["customer_id"].upper() == customer_id.upper()]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if priority:
        results = [r for r in results if _match(r, "priority", priority)]
    if channel:
        results = [r for r in results if _match(r, "channel", channel)]
    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
