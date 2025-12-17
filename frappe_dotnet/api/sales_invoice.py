"""
Sales Invoice API for ERPNext Integration
Handles invoice creation, customer management, and QR code updates
"""

import frappe
from frappe import _
from frappe.utils import nowdate, flt
import json


@frappe.whitelist(allow_guest=False)
def create_sales_invoice(**kwargs):
	"""
	Create a Sales Invoice with automatic customer and item creation if needed

	Required Parameters:
	- company: Company name
	- customer_name: Customer name (will be created if doesn't exist)
	- items: List of items with item_code, qty, rate (items will be created if they don't exist)

	Optional Parameters:
	- customer_email: Customer email
	- customer_phone: Customer mobile number
	- customer_group: Default is "Commercial"
	- customer_type: Default is "Company"
	- territory: Default is "All Territories"
	- custom_vat_registration_number: VAT registration number
	- commercial_registration_number: Commercial registration number
	- address_line1: Address line 1
	- address_line2: Address line 2
	- custom_building_number: Building number
	- custom_area: Area/District
	- city: City
	- county: County
	- state: State
	- pincode: Postal/ZIP code
	- posting_date: Default is today
	- due_date: Payment due date
	- qr_code: QR code data for ZATCA compliance
	- additional_fields: Dictionary of custom field values

	Optional Item Fields (for auto-creation):
	- items[].item_name: Item name (defaults to item_code)
	- items[].item_group: Item group (defaults to "Products")
	- items[].uom: Unit of measure (defaults to "Nos")
	- items[].item_tax_template: Tax template for the item
	- items[].tax_category: Tax category for the item

	Returns:
	- success: Boolean
	- message: Success or error message
	- invoice_name: Created invoice name
	- invoice_url: URL to view invoice
	"""
	try:
		# Validate API key authentication
		_validate_api_auth()

		# Parse arguments
		data = _parse_request_data(kwargs)

		# Validate required fields
		_validate_required_fields(data)

		# Get or create customer
		customer = _get_or_create_customer(data)

		# Create sales invoice
		invoice = _create_invoice(data, customer)

		# Update QR code if provided
		if data.get("qr_code"):
			_update_qr_code(invoice.name, data.get("qr_code"))

		# Commit the transaction
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Sales Invoice {0} created successfully").format(invoice.name),
			"invoice_name": invoice.name,
			"invoice_url": frappe.utils.get_url_to_form("Sales Invoice", invoice.name),
			"customer": customer,
			"grand_total": invoice.grand_total
		}

	except frappe.ValidationError as e:
		frappe.db.rollback()
		return _error_response(_("Validation Error: {0}").format(str(e)))
	except frappe.PermissionError as e:
		frappe.db.rollback()
		return _error_response(_("Permission Denied: You don't have permission to create invoices for this company"))
	except frappe.DoesNotExistError as e:
		frappe.db.rollback()
		return _error_response(_("Not Found: {0}").format(str(e)))
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(message=frappe.get_traceback(), title="Sales Invoice Creation Failed")
		return _error_response(_("Failed to create invoice: {0}").format(str(e)))


def _validate_api_auth():
	"""Validate API key authentication"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication required. Please provide valid API credentials."), frappe.AuthenticationError)


def _parse_request_data(kwargs):
	"""Parse and normalize request data"""
	data = frappe._dict(kwargs)

	# If items not in kwargs, try to get from request JSON body
	# Frappe doesn't always pass nested arrays through kwargs
	if not data.get("items") and frappe.request and frappe.request.data:
		try:
			request_json = json.loads(frappe.request.data)
			if isinstance(request_json, dict):
				# Merge request JSON with kwargs (kwargs takes precedence for non-items)
				for key, value in request_json.items():
					if key not in data or data[key] is None:
						data[key] = value
		except (json.JSONDecodeError, AttributeError):
			pass

	# Debug log to help troubleshoot data format issues
	frappe.log_error(
		message=f"Received kwargs: {type(kwargs)}\nItems type: {type(data.get('items'))}\nItems value: {data.get('items')}",
		title="Sales Invoice API - Request Data Debug"
	)

	# Handle items parsing - could come in various formats
	items = data.get("items")
	if items is None:
		# Items might not be in kwargs directly, could be in request data
		pass
	elif isinstance(items, str):
		# Items came as JSON string
		try:
			data.items = json.loads(items)
		except json.JSONDecodeError:
			frappe.throw(_("Invalid items data format. Expected JSON array."))
	elif isinstance(items, (list, tuple)):
		# Items came as a list/tuple - ensure each item is a dict
		parsed_items = []
		for item in items:
			if isinstance(item, str):
				try:
					parsed_items.append(json.loads(item))
				except json.JSONDecodeError:
					parsed_items.append(item)
			elif isinstance(item, dict):
				parsed_items.append(item)
			else:
				parsed_items.append(item)
		data.items = parsed_items
	elif isinstance(items, dict):
		# Single item passed as dict - convert to list
		data.items = [items]

	# Handle additional_fields parsing
	if isinstance(data.get("additional_fields"), str):
		try:
			data.additional_fields = json.loads(data.additional_fields)
		except json.JSONDecodeError:
			frappe.throw(_("Invalid additional_fields data format. Expected JSON object."))

	return data


def _validate_required_fields(data):
	"""Validate all required fields are present"""
	required_fields = ["company", "customer_name", "items"]
	missing_fields = [field for field in required_fields if not data.get(field)]

	if missing_fields:
		frappe.throw(
			_("Missing required fields: {0}").format(", ".join(missing_fields)),
			frappe.MandatoryError
		)

	# Validate company exists
	if not frappe.db.exists("Company", data.company):
		frappe.throw(
			_("Company '{0}' does not exist. Please check the company name.").format(data.company),
			frappe.DoesNotExistError
		)

	# Validate items structure
	if not isinstance(data.items, list) or len(data.items) == 0:
		frappe.throw(_("Items must be a non-empty list"))

	for idx, item in enumerate(data.items, 1):
		if not isinstance(item, dict):
			frappe.throw(_("Item {0} must be a dictionary").format(idx))

		if not item.get("item_code"):
			frappe.throw(_("Item {0}: 'item_code' is required").format(idx))

		if not item.get("qty"):
			frappe.throw(_("Item {0}: 'qty' is required").format(idx))


def _get_or_create_customer(data):
	"""Get existing customer or create new one with address and custom fields"""
	customer_name = data.customer_name
	company = data.company

	# Search for existing customer by name
	existing_customer = frappe.db.get_value(
		"Customer",
		{"customer_name": customer_name},
		["name", "customer_name"],
		as_dict=True
	)

	if existing_customer:
		return existing_customer.name

	# Create new customer
	try:
		customer_doc = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": customer_name,
			"customer_type": data.get("customer_type", "Company"),
			"customer_group": data.get("customer_group", "Commercial"),
			"territory": data.get("territory", "All Territories"),
			"email_id": data.get("customer_email"),
			"mobile_no": data.get("customer_phone"),
			"default_company": company
		})

		# Add custom VAT registration number if provided
		if data.get("custom_vat_registration_number"):
			customer_doc.custom_vat_registration_number = data.get("custom_vat_registration_number")

		# Add Commercial Registration Number to custom_additional_ids child table if provided
		if data.get("commercial_registration_number"):
			# Check if custom_additional_ids field exists
			if customer_doc.meta.has_field("custom_additional_ids"):
				customer_doc.append("custom_additional_ids", {
					"type_name": "Commercial Registration Number",
					"type_code": "CRN",
					"value": data.get("commercial_registration_number")
				})

		customer_doc.insert(ignore_permissions=False)

		# Create address if address fields are provided
		if data.get("address_line1") or data.get("city"):
			_create_customer_address(customer_doc.name, data)

		frappe.msgprint(
			_("New customer '{0}' created successfully").format(customer_name),
			indicator="green",
			alert=True
		)

		return customer_doc.name

	except frappe.DuplicateEntryError:
		# Race condition: customer was created between check and insert
		return frappe.db.get_value("Customer", {"customer_name": customer_name}, "name")
	except Exception as e:
		frappe.throw(
			_("Failed to create customer '{0}': {1}").format(customer_name, str(e)),
			frappe.ValidationError
		)


def _create_customer_address(customer, data):
	"""Create address for the customer"""
	try:
		# Build address title
		address_title = f"{customer}-Billing"

		# Check if address already exists
		if frappe.db.exists("Address", {"address_title": address_title}):
			frappe.msgprint(
				_("Address already exists for customer {0}").format(customer),
				indicator="orange"
			)
			return

		# Create address document
		address = frappe.get_doc({
			"doctype": "Address",
			"address_title": address_title,
			"address_type": "Billing",
			"address_line1": data.get("address_line1", ""),
			"address_line2": data.get("address_line2", ""),
			"city": data.get("city", ""),
			"county": data.get("county", ""),
			"state": data.get("state", ""),
			"pincode": data.get("pincode", ""),
			"country": data.get("country", "Saudi Arabia")  # Default to Saudi Arabia
		})

		# Add custom fields if they exist in Address doctype
		if data.get("custom_building_number"):
			if address.meta.has_field("custom_building_number"):
				address.custom_building_number = data.get("custom_building_number")

		if data.get("custom_area"):
			if address.meta.has_field("custom_area"):
				address.custom_area = data.get("custom_area")

		# Link address to customer
		address.append("links", {
			"link_doctype": "Customer",
			"link_name": customer
		})

		address.insert(ignore_permissions=False)

		frappe.msgprint(
			_("Address created for customer {0}").format(customer),
			indicator="green",
			alert=True
		)

		return address.name

	except Exception as e:
		# Log error but don't fail the customer creation
		frappe.log_error(
			message=f"Failed to create address for customer {customer}: {str(e)}",
			title="Customer Address Creation Failed"
		)
		frappe.msgprint(
			_("Customer created but address creation failed: {0}").format(str(e)),
			indicator="orange",
			alert=True
		)


def _create_invoice(data, customer):
	"""Create the sales invoice document"""
	try:
		invoice = frappe.get_doc({
			"doctype": "Sales Invoice",
			"company": data.company,
			"customer": customer,
			"posting_date": data.get("posting_date", nowdate()),
			"due_date": data.get("due_date"),
			"currency": data.get("currency") or frappe.get_cached_value("Company", data.company, "default_currency"),
			"items": []
		})

		# Add items
		for item_data in data.items:
			_add_invoice_item(invoice, item_data, data.company)

		# Add additional custom fields
		if data.get("additional_fields"):
			for field, value in data.additional_fields.items():
				if invoice.meta.has_field(field):
					invoice.set(field, value)

		# Insert and submit if requested
		invoice.insert(ignore_permissions=False)

		if data.get("submit_invoice"):
			invoice.submit()

		return invoice

	except Exception as e:
		error_msg = str(e)

		# Provide user-friendly error messages
		if "does not exist" in error_msg.lower():
			frappe.throw(
				_("One or more items in the invoice do not exist. Please verify all item codes."),
				frappe.DoesNotExistError
			)
		elif "permission" in error_msg.lower():
			frappe.throw(
				_("You don't have permission to create invoices. Please contact your administrator."),
				frappe.PermissionError
			)
		else:
			frappe.throw(
				_("Failed to create invoice: {0}").format(error_msg),
				frappe.ValidationError
			)


def _auto_create_item(item_code, item_data, company):
	"""Automatically create an item if it doesn't exist"""
	try:
		# Determine item group
		item_group = item_data.get("item_group", "Products")

		# Verify item group exists
		if not frappe.db.exists("Item Group", item_group):
			item_group = "All Item Groups"

		# Create the item
		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": item_code,
			"item_name": item_data.get("item_name") or item_code,
			"item_group": item_group,
			"description": item_data.get("description") or item_code,
			"stock_uom": item_data.get("uom", "Nos"),
			"is_stock_item": 1,
			"maintain_stock": 1,
			"standard_rate": flt(item_data.get("rate", 0)),
			"valuation_rate": flt(item_data.get("rate", 0))
		})

		# Add item tax template if provided
		if item_data.get("item_tax_template"):
			if frappe.db.exists("Item Tax Template", item_data.get("item_tax_template")):
				item.append("taxes", {
					"item_tax_template": item_data.get("item_tax_template"),
					"tax_category": item_data.get("tax_category")
				})

		# Add company defaults
		item.append("item_defaults", {
			"company": company,
			"default_warehouse": item_data.get("warehouse") or _get_default_warehouse(company),
			"income_account": item_data.get("income_account"),
			"expense_account": item_data.get("expense_account")
		})

		# Insert item
		item.insert(ignore_permissions=False)

		return item

	except Exception as e:
		frappe.log_error(
			message=f"Failed to auto-create item {item_code}: {str(e)}\n{frappe.get_traceback()}",
			title="Item Auto-Creation Failed"
		)
		# If auto-creation fails, throw error to stop invoice creation
		frappe.throw(
			_("Failed to create item '{0}': {1}").format(item_code, str(e)),
			frappe.ValidationError
		)


def _add_invoice_item(invoice, item_data, company):
	"""Add an item to the invoice"""
	item_code = item_data.get("item_code")

	# Check if item exists, if not create it
	if not frappe.db.exists("Item", item_code):
		# Auto-create the item
		item = _auto_create_item(item_code, item_data, company)
		frappe.msgprint(
			_("Item '{0}' created automatically").format(item_code),
			indicator="green",
			alert=True
		)
	else:
		# Get existing item details
		item = frappe.get_cached_doc("Item", item_code)

	# Determine rate
	rate = flt(item_data.get("rate"))
	if not rate:
		rate = flt(item_data.get("price_list_rate", 0))

	invoice.append("items", {
		"item_code": item_code,
		"item_name": item_data.get("item_name") or item.item_name,
		"description": item_data.get("description") or item.description,
		"qty": flt(item_data.get("qty", 1)),
		"uom": item_data.get("uom") or item.stock_uom,
		"rate": rate,
		"warehouse": item_data.get("warehouse") or _get_default_warehouse(company),
		"income_account": item_data.get("income_account"),
		"cost_center": item_data.get("cost_center"),
		"discount_percentage": flt(item_data.get("discount_percentage", 0))
	})


def _get_default_warehouse(company):
	"""Get default warehouse for the company"""
	warehouse = frappe.db.get_value(
		"Warehouse",
		{"company": company, "is_group": 0},
		"name"
	)
	return warehouse


def _update_qr_code(invoice_name, qr_code_data):
	"""Update QR code field in Sales Invoice"""
	try:
		# Check if custom field exists
		if not frappe.db.exists("Custom Field", {"dt": "Sales Invoice", "fieldname": "qr_code"}):
			frappe.msgprint(
				_("QR Code field does not exist in Sales Invoice. Please create it first."),
				indicator="orange",
				alert=True
			)
			return

		frappe.db.set_value("Sales Invoice", invoice_name, "qr_code", qr_code_data)
		frappe.msgprint(_("QR Code updated successfully"), indicator="green")

	except Exception as e:
		frappe.log_error(
			message=f"Failed to update QR code for {invoice_name}: {str(e)}",
			title="QR Code Update Failed"
		)


def _error_response(message):
	"""Return standardized error response"""
	return {
		"success": False,
		"message": message,
		"invoice_name": None
	}


@frappe.whitelist(allow_guest=False)
def update_invoice_qr_code(invoice_name, qr_code):
	"""
	Update QR code for an existing Sales Invoice

	Parameters:
	- invoice_name: Sales Invoice ID
	- qr_code: QR code data string

	Returns:
	- success: Boolean
	- message: Success or error message
	"""
	try:
		_validate_api_auth()

		if not invoice_name:
			return _error_response(_("Invoice name is required"))

		if not qr_code:
			return _error_response(_("QR code data is required"))

		if not frappe.db.exists("Sales Invoice", invoice_name):
			return _error_response(_("Sales Invoice '{0}' does not exist").format(invoice_name))

		_update_qr_code(invoice_name, qr_code)
		frappe.db.commit()

		return {
			"success": True,
			"message": _("QR Code updated successfully for invoice {0}").format(invoice_name)
		}

	except Exception as e:
		frappe.db.rollback()
		return _error_response(_("Failed to update QR code: {0}").format(str(e)))
