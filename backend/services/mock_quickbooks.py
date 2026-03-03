"""
Mock QuickBooks service for the Belfanti CNC Manufacturing POC.
Simulates estimates, invoices, purchase orders, sales orders, and products.
All data stored in-memory with incrementing document numbers.
"""

import uuid
from datetime import datetime


class MockQuickBooksService:
    """Simulates QuickBooks Online API interactions."""

    _products: dict[str, dict] = {}
    _estimates: dict[str, dict] = {}
    _invoices: dict[str, dict] = {}
    _purchase_orders: dict[str, dict] = {}
    _sales_orders: dict[str, dict] = {}

    _estimate_counter: int = 1001
    _po_counter: int = 2001
    _so_counter: int = 3001
    _invoice_counter: int = 4001
    _product_counter: int = 1

    # ------------------------------------------------------------------
    # Products
    # ------------------------------------------------------------------

    @classmethod
    def create_product(
        cls,
        name: str,
        description: str,
        unit_price: float,
        sku: str | None = None,
    ) -> dict:
        """Create a product/service item in QuickBooks.

        Args:
            name: Product name.
            description: Product description.
            unit_price: Price per unit.
            sku: Optional stock-keeping unit code.

        Returns:
            Dict with product_id, name, sku, unit_price, and status.
        """
        product_id = f"qb-prod-{uuid.uuid4().hex[:8]}"
        generated_sku = sku or f"SKU-{cls._product_counter:04d}"
        cls._product_counter += 1

        product = {
            "product_id": product_id,
            "name": name,
            "description": description,
            "sku": generated_sku,
            "unit_price": unit_price,
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }
        cls._products[product_id] = product

        print(f"[MockQB] Product created -> {name} (SKU: {generated_sku}) @ ${unit_price:.2f}")
        return {
            "product_id": product_id,
            "name": name,
            "sku": generated_sku,
            "unit_price": unit_price,
            "status": "active",
        }

    # ------------------------------------------------------------------
    # Estimates
    # ------------------------------------------------------------------

    @classmethod
    def create_estimate(
        cls,
        customer_name: str,
        line_items: list[dict],
        notes: str | None = None,
    ) -> dict:
        """Create a QuickBooks estimate (quote) for a customer.

        Args:
            customer_name: Name of the customer.
            line_items: List of dicts with description, quantity, unit_price, amount.
            notes: Optional notes for the estimate.

        Returns:
            Dict with estimate details including subtotal and total.
        """
        estimate_id = f"qb-est-{uuid.uuid4().hex[:8]}"
        estimate_number = f"EST-{cls._estimate_counter}"
        cls._estimate_counter += 1

        # Ensure each line item has an amount calculated
        processed_items = []
        for item in line_items:
            amount = item.get("amount", item.get("quantity", 1) * item.get("unit_price", 0))
            processed_items.append({
                "description": item.get("description", ""),
                "quantity": item.get("quantity", 1),
                "unit_price": item.get("unit_price", 0.0),
                "amount": round(amount, 2),
            })

        subtotal = round(sum(item["amount"] for item in processed_items), 2)
        total = subtotal  # No tax at estimate stage

        estimate = {
            "estimate_id": estimate_id,
            "estimate_number": estimate_number,
            "customer": customer_name,
            "line_items": processed_items,
            "subtotal": subtotal,
            "total": total,
            "status": "pending",
            "notes": notes,
            "created_at": datetime.now().isoformat(),
        }
        cls._estimates[estimate_id] = estimate

        print(f"[MockQB] Estimate {estimate_number} created for {customer_name} -> ${total:.2f}")
        return {
            "estimate_id": estimate_id,
            "estimate_number": estimate_number,
            "customer": customer_name,
            "line_items": processed_items,
            "subtotal": subtotal,
            "total": total,
            "status": "pending",
        }

    @classmethod
    def generate_estimate_pdf(cls, estimate_id: str) -> dict:
        """Generate a PDF for a QuickBooks estimate.

        Args:
            estimate_id: The estimate identifier.

        Returns:
            Dict with pdf_url and filename.
        """
        estimate = cls._estimates.get(estimate_id)
        estimate_number = estimate["estimate_number"] if estimate else "UNKNOWN"
        filename = f"{estimate_number}.pdf"

        print(f"[MockQB] PDF generated for estimate {estimate_id} -> {filename}")
        return {
            "pdf_url": f"https://quickbooks.mock/estimates/{estimate_id}.pdf",
            "filename": filename,
        }

    @classmethod
    def send_estimate_email(
        cls,
        estimate_id: str,
        to_email: str,
        message: str | None = None,
    ) -> dict:
        """Email a QuickBooks estimate to the customer.

        Args:
            estimate_id: The estimate identifier.
            to_email: Recipient email address.
            message: Optional custom message body.

        Returns:
            Dict with send status, recipient, and estimate_id.
        """
        # Update estimate status
        if estimate_id in cls._estimates:
            cls._estimates[estimate_id]["status"] = "sent"

        print(f"[MockQB] Estimate {estimate_id} emailed to {to_email}")
        return {
            "status": "sent",
            "to": to_email,
            "estimate_id": estimate_id,
        }

    @classmethod
    def convert_estimate_to_invoice(cls, estimate_id: str) -> dict:
        """Convert an accepted estimate into an invoice.

        Args:
            estimate_id: The estimate to convert.

        Returns:
            Dict with invoice_id, estimate_id, and status.
        """
        invoice_id = f"qb-inv-{uuid.uuid4().hex[:8]}"
        invoice_number = f"INV-{cls._invoice_counter}"
        cls._invoice_counter += 1

        estimate = cls._estimates.get(estimate_id, {})
        invoice = {
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "estimate_id": estimate_id,
            "customer": estimate.get("customer", ""),
            "line_items": estimate.get("line_items", []),
            "total": estimate.get("total", 0.0),
            "status": "converted",
            "created_at": datetime.now().isoformat(),
        }
        cls._invoices[invoice_id] = invoice

        if estimate_id in cls._estimates:
            cls._estimates[estimate_id]["status"] = "accepted"

        print(f"[MockQB] Estimate {estimate_id} converted to Invoice {invoice_number}")
        return {
            "invoice_id": invoice_id,
            "estimate_id": estimate_id,
            "status": "converted",
        }

    # ------------------------------------------------------------------
    # Purchase Orders
    # ------------------------------------------------------------------

    @classmethod
    def create_purchase_order(
        cls,
        vendor_name: str,
        line_items: list[dict],
        notes: str | None = None,
    ) -> dict:
        """Create a purchase order for a material vendor.

        Args:
            vendor_name: Name of the vendor.
            line_items: List of dicts with description, quantity, unit_price, amount.
            notes: Optional notes.

        Returns:
            Dict with po_id, po_number, vendor, total, and status.
        """
        po_id = f"qb-po-{uuid.uuid4().hex[:8]}"
        po_number = f"PO-{cls._po_counter}"
        cls._po_counter += 1

        processed_items = []
        for item in line_items:
            amount = item.get("amount", item.get("quantity", 1) * item.get("unit_price", 0))
            processed_items.append({
                "description": item.get("description", ""),
                "quantity": item.get("quantity", 1),
                "unit_price": item.get("unit_price", 0.0),
                "amount": round(amount, 2),
            })

        total = round(sum(item["amount"] for item in processed_items), 2)

        po = {
            "po_id": po_id,
            "po_number": po_number,
            "vendor": vendor_name,
            "line_items": processed_items,
            "total": total,
            "status": "draft",
            "notes": notes,
            "created_at": datetime.now().isoformat(),
        }
        cls._purchase_orders[po_id] = po

        print(f"[MockQB] Purchase Order {po_number} created for {vendor_name} -> ${total:.2f}")
        return {
            "po_id": po_id,
            "po_number": po_number,
            "vendor": vendor_name,
            "total": total,
            "status": "draft",
        }

    # ------------------------------------------------------------------
    # Sales Orders
    # ------------------------------------------------------------------

    @classmethod
    def create_sales_order(
        cls,
        customer_name: str,
        estimate_id: str,
        line_items: list[dict],
    ) -> dict:
        """Create a sales order from an accepted estimate.

        Args:
            customer_name: Customer name.
            estimate_id: The originating estimate ID.
            line_items: List of line item dicts.

        Returns:
            Dict with so_id, so_number, customer, total, and status.
        """
        so_id = f"qb-so-{uuid.uuid4().hex[:8]}"
        so_number = f"SO-{cls._so_counter}"
        cls._so_counter += 1

        processed_items = []
        for item in line_items:
            amount = item.get("amount", item.get("quantity", 1) * item.get("unit_price", 0))
            processed_items.append({
                "description": item.get("description", ""),
                "quantity": item.get("quantity", 1),
                "unit_price": item.get("unit_price", 0.0),
                "amount": round(amount, 2),
            })

        total = round(sum(item["amount"] for item in processed_items), 2)

        so = {
            "so_id": so_id,
            "so_number": so_number,
            "customer": customer_name,
            "estimate_id": estimate_id,
            "line_items": processed_items,
            "total": total,
            "status": "open",
            "created_at": datetime.now().isoformat(),
        }
        cls._sales_orders[so_id] = so

        print(f"[MockQB] Sales Order {so_number} created for {customer_name} -> ${total:.2f}")
        return {
            "so_id": so_id,
            "so_number": so_number,
            "customer": customer_name,
            "total": total,
            "status": "open",
        }

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    @classmethod
    def get_estimate(cls, estimate_id: str) -> dict | None:
        """Retrieve an estimate by ID."""
        return cls._estimates.get(estimate_id)

    @classmethod
    def get_purchase_order(cls, po_id: str) -> dict | None:
        """Retrieve a purchase order by ID."""
        return cls._purchase_orders.get(po_id)

    @classmethod
    def get_sales_order(cls, so_id: str) -> dict | None:
        """Retrieve a sales order by ID."""
        return cls._sales_orders.get(so_id)

    @classmethod
    def reset(cls) -> None:
        """Clear all stored data. Useful for testing."""
        cls._products.clear()
        cls._estimates.clear()
        cls._invoices.clear()
        cls._purchase_orders.clear()
        cls._sales_orders.clear()
        cls._estimate_counter = 1001
        cls._po_counter = 2001
        cls._so_counter = 3001
        cls._invoice_counter = 4001
        cls._product_counter = 1
