"""
Item API for ERPNext Integration
Handles item creation with tax templates and tax categories
"""

import frappe
from frappe import _
from frappe.utils import cstr
import json


@frappe.whitelist(allow_guest=False)
def create_item(**kwargs):
	"""
	Create an Item with tax templates and tax categories

	Required Parameters:
	- item_code: Unique item code
	- item_name: Item name
	- item_group: Item group (must exist)

	Optional Parameters:
	- description: Item description
	- stock_uom: Stock UOM (default: Nos)
	- standard_rate: Standard selling rate
	- valuation_rate: Valuation rate
	- opening_stock: Opening stock quantity
	- is_stock_item: 1 or 0 (default: 1)
	- maintain_stock: 1 or 0 (default: 1)
	- company: Company for tax template mapping
	- tax_category: Tax category (e.g., VAT-GSS)
	- item_tax_template: Item tax template name (e.g., VAT 15 - GSS)
	- tax_templates: List of tax templates with company mapping
	- item_defaults: List of company-specific defaults

	Returns:
	- success: Boolean
	- message: Success or error message
	- item_code: Created item code
	- item_url: URL to view item
	"""
	try:
		# Validate API key authentication
		_validate_api_auth()

		# Parse arguments
		data = _parse_request_data(kwargs)

		# Validate required fields
		_validate_required_fields(data)

		# Create item
		item = _create_item_doc(data)

		# Commit the transaction
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Item {0} created successfully").format(item.item_code),
			"item_code": item.item_code,
			"item_name": item.item_name,
			"item_url": frappe.utils.get_url_to_form("Item", item.name)
		}

	except frappe.ValidationError as e:
		frappe.db.rollback()
		return _error_response(_("Validation Error: {0}").format(str(e)))
	except frappe.PermissionError as e:
		frappe.db.rollback()
		return _error_response(_("Permission Denied: You don't have permission to create items"))
	except frappe.DuplicateEntryError as e:
		frappe.db.rollback()
		return _error_response(_("Item code '{0}' already exists").format(data.get("item_code")))
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(message=frappe.get_traceback(), title="Item Creation Failed")
		return _error_response(_("Failed to create item: {0}").format(str(e)))


def _validate_api_auth():
	"""Validate API key authentication"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication required. Please provide valid API credentials."), frappe.AuthenticationError)


def _parse_request_data(kwargs):
	"""Parse and normalize request data"""
	data = frappe._dict(kwargs)

	# Parse JSON strings if needed
	if isinstance(data.get("tax_templates"), str):
		try:
			data.tax_templates = json.loads(data.tax_templates)
		except json.JSONDecodeError:
			frappe.throw(_("Invalid tax_templates data format. Expected JSON array."))

	if isinstance(data.get("item_defaults"), str):
		try:
			data.item_defaults = json.loads(data.item_defaults)
		except json.JSONDecodeError:
			frappe.throw(_("Invalid item_defaults data format. Expected JSON array."))

	return data


def _validate_required_fields(data):
	"""Validate all required fields are present"""
	required_fields = ["item_code", "item_name", "item_group"]
	missing_fields = [field for field in required_fields if not data.get(field)]

	if missing_fields:
		frappe.throw(
			_("Missing required fields: {0}").format(", ".join(missing_fields)),
			frappe.MandatoryError
		)

	# Validate item_group exists
	if not frappe.db.exists("Item Group", data.item_group):
		frappe.throw(
			_("Item Group '{0}' does not exist. Please check the item group.").format(data.item_group),
			frappe.DoesNotExistError
		)

	# Validate item_code doesn't already exist
	if frappe.db.exists("Item", data.item_code):
		frappe.throw(
			_("Item code '{0}' already exists").format(data.item_code),
			frappe.DuplicateEntryError
		)


def _create_item_doc(data):
	"""Create the item document"""
	try:
		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": data.item_code,
			"item_name": data.item_name,
			"item_group": data.item_group,
			"description": data.get("description") or data.item_name,
			"stock_uom": data.get("stock_uom", "Nos"),
			"is_stock_item": data.get("is_stock_item", 1),
			"maintain_stock": data.get("maintain_stock", 1),
			"include_item_in_manufacturing": data.get("include_item_in_manufacturing", 0),
			"opening_stock": data.get("opening_stock", 0),
			"valuation_rate": data.get("valuation_rate", 0),
			"standard_rate": data.get("standard_rate", 0),
			"disabled": 0
		})

		# Add item tax templates
		if data.get("tax_templates"):
			_add_tax_templates(item, data.tax_templates)
		elif data.get("item_tax_template") and data.get("company"):
			# Single tax template for a company
			_add_single_tax_template(item, data.get("item_tax_template"), data.get("tax_category"))

		# Add item defaults (company-specific settings)
		if data.get("item_defaults"):
			_add_item_defaults(item, data.item_defaults)
		elif data.get("company"):
			# Single company default
			_add_single_item_default(item, data)

		# Insert item
		item.insert(ignore_permissions=False)

		frappe.msgprint(
			_("Item '{0}' created successfully").format(data.item_code),
			indicator="green",
			alert=True
		)

		return item

	except Exception as e:
		error_msg = str(e)

		# Provide user-friendly error messages
		if "duplicate" in error_msg.lower():
			frappe.throw(
				_("Item code '{0}' already exists").format(data.item_code),
				frappe.DuplicateEntryError
			)
		elif "permission" in error_msg.lower():
			frappe.throw(
				_("You don't have permission to create items. Please contact your administrator."),
				frappe.PermissionError
			)
		else:
			frappe.throw(
				_("Failed to create item: {0}").format(error_msg),
				frappe.ValidationError
			)


def _add_tax_templates(item, tax_templates):
	"""Add multiple tax templates to item"""
	for template in tax_templates:
		if not isinstance(template, dict):
			continue

		item_tax_template = template.get("item_tax_template")
		tax_category = template.get("tax_category")

		# Validate tax template exists
		if item_tax_template and not frappe.db.exists("Item Tax Template", item_tax_template):
			frappe.msgprint(
				_("Item Tax Template '{0}' does not exist. Skipping.").format(item_tax_template),
				indicator="orange",
				alert=True
			)
			continue

		# Validate tax category exists
		if tax_category and not frappe.db.exists("Tax Category", tax_category):
			frappe.msgprint(
				_("Tax Category '{0}' does not exist. Skipping.").format(tax_category),
				indicator="orange",
				alert=True
			)
			continue

		item.append("taxes", {
			"item_tax_template": item_tax_template,
			"tax_category": tax_category,
			"valid_from": template.get("valid_from"),
			"minimum_net_rate": template.get("minimum_net_rate", 0),
			"maximum_net_rate": template.get("maximum_net_rate", 0)
		})


def _add_single_tax_template(item, item_tax_template, tax_category=None):
	"""Add a single tax template to item"""
	# Validate tax template exists
	if not frappe.db.exists("Item Tax Template", item_tax_template):
		frappe.msgprint(
			_("Item Tax Template '{0}' does not exist").format(item_tax_template),
			indicator="orange",
			alert=True
		)
		return

	# Validate tax category if provided
	if tax_category and not frappe.db.exists("Tax Category", tax_category):
		frappe.msgprint(
			_("Tax Category '{0}' does not exist").format(tax_category),
			indicator="orange",
			alert=True
		)
		tax_category = None

	item.append("taxes", {
		"item_tax_template": item_tax_template,
		"tax_category": tax_category
	})


def _add_item_defaults(item, item_defaults):
	"""Add multiple company defaults to item"""
	for default in item_defaults:
		if not isinstance(default, dict):
			continue

		company = default.get("company")

		# Validate company exists
		if not company or not frappe.db.exists("Company", company):
			frappe.msgprint(
				_("Company '{0}' does not exist. Skipping.").format(company),
				indicator="orange",
				alert=True
			)
			continue

		item.append("item_defaults", {
			"company": company,
			"default_warehouse": default.get("default_warehouse"),
			"default_price_list": default.get("default_price_list"),
			"buying_cost_center": default.get("buying_cost_center"),
			"selling_cost_center": default.get("selling_cost_center"),
			"expense_account": default.get("expense_account"),
			"income_account": default.get("income_account")
		})


def _add_single_item_default(item, data):
	"""Add a single company default to item"""
	company = data.get("company")

	# Validate company exists
	if not company or not frappe.db.exists("Company", company):
		frappe.msgprint(
			_("Company '{0}' does not exist").format(company),
			indicator="orange",
			alert=True
		)
		return

	item.append("item_defaults", {
		"company": company,
		"default_warehouse": data.get("default_warehouse"),
		"default_price_list": data.get("default_price_list"),
		"buying_cost_center": data.get("buying_cost_center"),
		"selling_cost_center": data.get("selling_cost_center"),
		"expense_account": data.get("expense_account"),
		"income_account": data.get("income_account")
	})


def _error_response(message):
	"""Return standardized error response"""
	return {
		"success": False,
		"message": message,
		"item_code": None
	}


@frappe.whitelist(allow_guest=False)
def get_tax_templates(company=None):
	"""
	Get available tax templates, optionally filtered by company

	Parameters:
	- company: Optional company name to filter templates

	Returns:
	- success: Boolean
	- tax_templates: List of available tax templates
	"""
	try:
		_validate_api_auth()

		filters = {}
		if company:
			filters["company"] = company

		templates = frappe.get_all(
			"Item Tax Template",
			filters=filters,
			fields=["name", "title", "company"],
			order_by="name"
		)

		return {
			"success": True,
			"tax_templates": templates
		}

	except Exception as e:
		return _error_response(str(e))


@frappe.whitelist(allow_guest=False)
def get_tax_categories():
	"""
	Get available tax categories

	Returns:
	- success: Boolean
	- tax_categories: List of available tax categories
	"""
	try:
		_validate_api_auth()

		categories = frappe.get_all(
			"Tax Category",
			fields=["name", "title", "disabled"],
			filters={"disabled": 0},
			order_by="name"
		)

		return {
			"success": True,
			"tax_categories": categories
		}

	except Exception as e:
		return _error_response(str(e))


@frappe.whitelist(allow_guest=False)
def get_item_groups():
	"""
	Get available item groups

	Returns:
	- success: Boolean
	- item_groups: List of available item groups
	"""
	try:
		_validate_api_auth()

		groups = frappe.get_all(
			"Item Group",
			fields=["name", "parent_item_group", "is_group"],
			order_by="name"
		)

		return {
			"success": True,
			"item_groups": groups
		}

	except Exception as e:
		return _error_response(str(e))
