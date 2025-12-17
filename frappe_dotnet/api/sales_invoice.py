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

	Tax Options (use one of these):
	- taxes_and_charges: Name of Sales Taxes and Charges Template (e.g., "Saudi VAT 15%")
	- taxes: Custom array of tax entries:
		[{"charge_type": "On Net Total", "account_head": "VAT 15% - GSS", "rate": 15, "description": "VAT 15%"}]
	- If neither provided, uses company's default tax template

	Optional Item Fields (for auto-creation):
	- items[].item_name: Item name (defaults to item_code)
	- items[].item_group: Item group (defaults to "Products")
	- items[].uom: Unit of measure (defaults to "Nos")
	- items[].item_tax_template: Item Tax Template name (e.g., "VAT 15% - GSS")
	- items[].tax_code: ZATCA tax category code - auto-maps to Item Tax Template:
		- "S" or "01" or "05" = Standard Rate 15%
		- "Z" or "02" = Zero Rated 0%
		- "E" or "03" = Exempt
		- "O" or "04" = Out of Scope
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

	# Always try to get data from request JSON body
	# Frappe doesn't always pass nested arrays through kwargs properly
	request_json = None
	if frappe.request:
		try:
			# Try using Flask's get_json() first (handles content-type and encoding)
			if hasattr(frappe.request, 'get_json'):
				request_json = frappe.request.get_json(silent=True)

			# Fallback to manual parsing if get_json didn't work
			if not request_json and frappe.request.data:
				raw_data = frappe.request.data
				# Handle bytes
				if isinstance(raw_data, bytes):
					raw_data = raw_data.decode('utf-8')
				if raw_data:
					request_json = json.loads(raw_data)
		except (json.JSONDecodeError, AttributeError, UnicodeDecodeError) as e:
			frappe.log_error(
				message=f"Failed to parse request JSON: {str(e)}\nRaw data type: {type(frappe.request.data)}\nRaw data: {frappe.request.data}",
				title="Sales Invoice API - JSON Parse Error"
			)

	# Merge request JSON with data
	if request_json and isinstance(request_json, dict):
		for key, value in request_json.items():
			# Always use request body for items since kwargs doesn't handle arrays well
			if key == "items" or key not in data or data.get(key) is None:
				data[key] = value

	# Debug log to help troubleshoot data format issues
	frappe.log_error(
		message=f"Received kwargs keys: {list(kwargs.keys())}\nItems type: {type(data.get('items'))}\nItems value: {data.get('items')}\nRequest JSON: {request_json}",
		title="Sales Invoice API - Request Data Debug"
	)

	# Handle items parsing - could come in various formats
	# Use dictionary key access instead of attribute to avoid conflict with dict.items() method
	items = data.get("items")
	if items is None:
		# Items might not be in kwargs directly, could be in request data
		pass
	elif isinstance(items, str):
		# Items came as JSON string
		try:
			data["items"] = json.loads(items)
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
		data["items"] = parsed_items
	elif isinstance(items, dict):
		# Single item passed as dict - convert to list
		data["items"] = [items]

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
	# Use data["items"] or data.get("items") to avoid conflict with dict.items() method
	invoice_items = data.get("items")
	if not isinstance(invoice_items, list) or len(invoice_items) == 0:
		frappe.throw(_("Items must be a non-empty list"))

	for idx, item in enumerate(invoice_items, 1):
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
			"country": data.get("country", "Saudi Arabia"),  # Default to Saudi Arabia
			"is_primary_address": 1,  # Set as Preferred Billing Address
			"is_shipping_address": 0
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


def _add_invoice_taxes(invoice, data):
	"""Add taxes to the invoice from template or custom taxes array

	Supports:
	1. taxes_and_charges: Name of Sales Taxes and Charges Template
	2. taxes: Custom array of tax entries with charge_type, account_head, rate, etc.

	Example taxes array:
	[
		{
			"charge_type": "On Net Total",
			"account_head": "VAT 15% - GSS",
			"rate": 15,
			"description": "VAT 15%"
		},
		{
			"charge_type": "On Net Total",
			"account_head": "VAT 0% - GSS",
			"rate": 0,
			"description": "Zero Rated"
		}
	]
	"""
	# Option 1: Use Sales Taxes and Charges Template
	if data.get("taxes_and_charges"):
		template_name = data.get("taxes_and_charges")
		if frappe.db.exists("Sales Taxes and Charges Template", template_name):
			invoice.taxes_and_charges = template_name
			# Get taxes from template
			template = frappe.get_doc("Sales Taxes and Charges Template", template_name)
			for tax in template.taxes:
				invoice.append("taxes", {
					"charge_type": tax.charge_type,
					"account_head": tax.account_head,
					"rate": tax.rate,
					"description": tax.description,
					"included_in_print_rate": tax.included_in_print_rate,
					"cost_center": tax.cost_center
				})
			return
		else:
			frappe.msgprint(
				_("Tax template '{0}' not found. Using custom taxes if provided.").format(template_name),
				indicator="orange"
			)

	# Option 2: Use custom taxes array
	taxes = data.get("taxes")
	if taxes and isinstance(taxes, list):
		for tax_data in taxes:
			if isinstance(tax_data, dict):
				# Validate required fields
				if not tax_data.get("account_head"):
					frappe.throw(_("Tax entry missing required field: account_head"))

				invoice.append("taxes", {
					"charge_type": tax_data.get("charge_type", "On Net Total"),
					"account_head": tax_data.get("account_head"),
					"rate": flt(tax_data.get("rate", 0)),
					"description": tax_data.get("description", ""),
					"included_in_print_rate": tax_data.get("included_in_print_rate", 0),
					"cost_center": tax_data.get("cost_center"),
					"tax_amount": flt(tax_data.get("tax_amount", 0)) if tax_data.get("tax_amount") else None
				})
		return

	# Option 3: Try to get default tax template from company
	default_template = frappe.db.get_value(
		"Sales Taxes and Charges Template",
		{"company": data.company, "is_default": 1},
		"name"
	)
	if default_template:
		invoice.taxes_and_charges = default_template
		template = frappe.get_doc("Sales Taxes and Charges Template", default_template)
		for tax in template.taxes:
			invoice.append("taxes", {
				"charge_type": tax.charge_type,
				"account_head": tax.account_head,
				"rate": tax.rate,
				"description": tax.description,
				"included_in_print_rate": tax.included_in_print_rate,
				"cost_center": tax.cost_center
			})


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
			"items": [],
			"taxes": []
		})

		# Add items
		for item_data in data.get("items"):
			_add_invoice_item(invoice, item_data, data.company)

		# Add taxes - either from template or custom taxes array
		_add_invoice_taxes(invoice, data)

		# Add additional custom fields
		if data.get("additional_fields"):
			for field, value in data.get("additional_fields").items():
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

	# Build item row
	item_row = {
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
	}

	# Handle item-level tax template
	# Supports: direct template name OR tax_code mapping (e.g., "01" = 0%, "05" = 15%)
	item_tax_template = _resolve_item_tax_template(item_data, company)
	if item_tax_template:
		item_row["item_tax_template"] = item_tax_template

	invoice.append("items", item_row)


def _resolve_item_tax_template(item_data, company):
	"""Resolve item tax template from direct name or tax code

	Supports:
	1. item_tax_template: Direct template name (e.g., "VAT 15% - GSS")
	2. tax_code: ZATCA tax category code that maps to template
	   - "01" or "S" = Standard Rate (15%)
	   - "02" or "Z" = Zero Rated (0%)
	   - "03" or "E" = Exempt
	   - "04" or "O" = Out of Scope
	   - "05" = Standard Rate 15% (legacy)

	The function searches for matching Item Tax Template by:
	1. Exact name match
	2. Template containing the tax code
	3. Template for the company with matching rate
	"""
	# Option 1: Direct template name provided
	if item_data.get("item_tax_template"):
		template_name = item_data.get("item_tax_template")
		# Check if it exists (with or without company suffix)
		if frappe.db.exists("Item Tax Template", template_name):
			return template_name
		# Try with company abbreviation
		company_abbr = frappe.get_cached_value("Company", company, "abbr")
		if company_abbr:
			template_with_company = f"{template_name} - {company_abbr}"
			if frappe.db.exists("Item Tax Template", template_with_company):
				return template_with_company

	# Option 2: Tax code provided - map to template
	tax_code = item_data.get("tax_code")
	if tax_code:
		return _get_tax_template_from_code(tax_code, company)

	return None


def _get_tax_template_from_code(tax_code, company):
	"""Map ZATCA tax category code to Item Tax Template

	ZATCA Tax Category Codes:
	- S / 01 / 05 = Standard Rate (15% VAT)
	- Z / 02 = Zero Rated (0% VAT)
	- E / 03 = Exempt
	- O / 04 = Out of Scope

	Returns the Item Tax Template name for the company
	"""
	# Normalize tax code
	tax_code = str(tax_code).upper().strip()

	# Map tax codes to search patterns and rates
	tax_code_mapping = {
		# Standard Rate 15%
		"S": {"patterns": ["15", "standard", "vat 15"], "rate": 15},
		"01": {"patterns": ["15", "standard", "vat 15"], "rate": 15},
		"05": {"patterns": ["15", "standard", "vat 15"], "rate": 15},
		# Zero Rated 0%
		"Z": {"patterns": ["0", "zero", "vat 0"], "rate": 0},
		"02": {"patterns": ["0", "zero", "vat 0"], "rate": 0},
		# Exempt
		"E": {"patterns": ["exempt", "0"], "rate": 0},
		"03": {"patterns": ["exempt", "0"], "rate": 0},
		# Out of Scope
		"O": {"patterns": ["out of scope", "oos", "0"], "rate": 0},
		"04": {"patterns": ["out of scope", "oos", "0"], "rate": 0},
	}

	mapping = tax_code_mapping.get(tax_code)
	if not mapping:
		return None

	company_abbr = frappe.get_cached_value("Company", company, "abbr")

	# Strategy 1: Find template by pattern match for this company
	templates = frappe.get_all(
		"Item Tax Template",
		filters={"company": company},
		fields=["name"]
	)

	for template in templates:
		template_name_lower = template.name.lower()
		for pattern in mapping["patterns"]:
			if pattern in template_name_lower:
				return template.name

	# Strategy 2: Find by tax rate in template
	for template in templates:
		template_doc = frappe.get_cached_doc("Item Tax Template", template.name)
		for tax_row in template_doc.taxes:
			if flt(tax_row.tax_rate) == mapping["rate"]:
				return template.name

	# Strategy 3: Try common naming conventions
	common_names = []
	if mapping["rate"] == 15:
		common_names = [
			f"VAT 15% - {company_abbr}",
			f"Saudi VAT 15% - {company_abbr}",
			f"Standard Rate - {company_abbr}",
			f"KSA VAT 15% - {company_abbr}",
		]
	elif mapping["rate"] == 0:
		common_names = [
			f"VAT 0% - {company_abbr}",
			f"Zero Rated - {company_abbr}",
			f"VAT Zero - {company_abbr}",
			f"Exempt - {company_abbr}",
		]

	for name in common_names:
		if frappe.db.exists("Item Tax Template", name):
			return name

	return None


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
