"""
Test client for Item API
Run this script to test the Item API endpoints
"""

import requests
import json
from typing import Dict, Any


class ItemAPIClient:
	"""Client for interacting with the Item API"""

	def __init__(self, site_url: str, api_key: str, api_secret: str):
		"""
		Initialize the API client

		Args:
			site_url: ERPNext site URL (e.g., https://your-site.com)
			api_key: API key from ERPNext user
			api_secret: API secret from ERPNext user
		"""
		self.site_url = site_url.rstrip('/')
		self.api_key = api_key
		self.api_secret = api_secret
		self.headers = {
			'Authorization': f'token {api_key}:{api_secret}',
			'Content-Type': 'application/json'
		}

	def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Create a new Item

		Args:
			item_data: Dictionary containing item details

		Returns:
			API response as dictionary
		"""
		url = f"{self.site_url}/api/method/frappe_dotnet.api.item.create_item"

		try:
			response = requests.post(url, json=item_data, headers=self.headers)
			response.raise_for_status()
			return response.json().get('message', {})
		except requests.exceptions.RequestException as e:
			print(f"Error creating item: {e}")
			if hasattr(e, 'response') and e.response is not None:
				return e.response.json()
			return {"success": False, "message": str(e)}

	def get_tax_templates(self, company: str = None) -> Dict[str, Any]:
		"""
		Get available tax templates

		Args:
			company: Optional company name to filter

		Returns:
			API response as dictionary
		"""
		url = f"{self.site_url}/api/method/frappe_dotnet.api.item.get_tax_templates"

		params = {}
		if company:
			params["company"] = company

		try:
			response = requests.get(url, headers=self.headers, params=params)
			response.raise_for_status()
			return response.json().get('message', {})
		except requests.exceptions.RequestException as e:
			print(f"Error getting tax templates: {e}")
			return {"success": False, "message": str(e)}

	def get_tax_categories(self) -> Dict[str, Any]:
		"""
		Get available tax categories

		Returns:
			API response as dictionary
		"""
		url = f"{self.site_url}/api/method/frappe_dotnet.api.item.get_tax_categories"

		try:
			response = requests.get(url, headers=self.headers)
			response.raise_for_status()
			return response.json().get('message', {})
		except requests.exceptions.RequestException as e:
			print(f"Error getting tax categories: {e}")
			return {"success": False, "message": str(e)}

	def get_item_groups(self) -> Dict[str, Any]:
		"""
		Get available item groups

		Returns:
			API response as dictionary
		"""
		url = f"{self.site_url}/api/method/frappe_dotnet.api.item.get_item_groups"

		try:
			response = requests.get(url, headers=self.headers)
			response.raise_for_status()
			return response.json().get('message', {})
		except requests.exceptions.RequestException as e:
			print(f"Error getting item groups: {e}")
			return {"success": False, "message": str(e)}


def test_get_configuration():
	"""Test getting tax templates, categories, and item groups"""
	# Load configuration
	with open('example_config.json', 'r') as f:
		config = json.load(f)

	# Initialize client
	client = ItemAPIClient(
		site_url=config['site_url'],
		api_key=config['api_key'],
		api_secret=config['api_secret']
	)

	print("=" * 60)
	print("GETTING CONFIGURATION DATA")
	print("=" * 60)

	# Get item groups
	print("\n1. Getting Item Groups...")
	groups = client.get_item_groups()
	if groups.get('success'):
		print(f"   Found {len(groups['item_groups'])} item groups:")
		for group in groups['item_groups'][:5]:  # Show first 5
			print(f"   - {group['name']}")
	else:
		print(f"   Error: {groups.get('message')}")

	# Get tax categories
	print("\n2. Getting Tax Categories...")
	categories = client.get_tax_categories()
	if categories.get('success'):
		print(f"   Found {len(categories['tax_categories'])} tax categories:")
		for cat in categories['tax_categories']:
			print(f"   - {cat['name']}")
	else:
		print(f"   Error: {categories.get('message')}")

	# Get tax templates
	print("\n3. Getting Tax Templates...")
	company = config['companies'][0]['name'] if config.get('companies') else None
	templates = client.get_tax_templates(company)
	if templates.get('success'):
		print(f"   Found {len(templates['tax_templates'])} tax templates:")
		for template in templates['tax_templates']:
			print(f"   - {template['name']} ({template.get('company', 'No Company')})")
	else:
		print(f"   Error: {templates.get('message')}")

	return groups, categories, templates


def test_create_basic_item():
	"""Test creating a basic item"""
	# Load configuration
	with open('example_config.json', 'r') as f:
		config = json.load(f)

	# Initialize client
	client = ItemAPIClient(
		site_url=config['site_url'],
		api_key=config['api_key'],
		api_secret=config['api_secret']
	)

	print("\n" + "=" * 60)
	print("TEST 1: Creating Basic Item")
	print("=" * 60)

	# Item data
	item_data = {
		"item_code": "TEST-BASIC-001",
		"item_name": "Basic Test Product",
		"item_group": "Products",  # Update with your item group
		"description": "Basic test product created via API",
		"stock_uom": "Nos",
		"standard_rate": 100.00,
		"is_stock_item": 1,
		"maintain_stock": 1
	}

	# Create item
	print("\nCreating item...")
	result = client.create_item(item_data)

	print("\nResponse:")
	print(json.dumps(result, indent=2))

	if result.get('success'):
		print(f"\n✓ Item created successfully: {result.get('item_code')}")
		print(f"  URL: {result.get('item_url')}")
	else:
		print(f"\n✗ Failed to create item: {result.get('message')}")

	return result


def test_create_vat_item():
	"""Test creating an item with VAT configuration"""
	# Load configuration
	with open('example_config.json', 'r') as f:
		config = json.load(f)

	# Initialize client
	client = ItemAPIClient(
		site_url=config['site_url'],
		api_key=config['api_key'],
		api_secret=config['api_secret']
	)

	print("\n" + "=" * 60)
	print("TEST 2: Creating Item with VAT")
	print("=" * 60)

	# Item data with VAT
	item_data = {
		"item_code": "TEST-VAT-001",
		"item_name": "VAT Test Product",
		"item_group": "Products",  # Update with your item group
		"description": "Product with VAT configuration",
		"stock_uom": "Nos",
		"standard_rate": 150.00,
		"company": "ZATCA Company",  # Update with your company
		"item_tax_template": "VAT 15 - GSS",  # Update with your tax template
		"tax_category": "VAT-GSS",  # Update with your tax category
		"default_warehouse": "Stores - ZATCA"  # Update with your warehouse
	}

	# Create item
	print("\nCreating item with VAT configuration...")
	result = client.create_item(item_data)

	print("\nResponse:")
	print(json.dumps(result, indent=2))

	if result.get('success'):
		print(f"\n✓ Item created successfully: {result.get('item_code')}")
		print(f"  URL: {result.get('item_url')}")
	else:
		print(f"\n✗ Failed to create item: {result.get('message')}")

	return result


def test_create_service_item():
	"""Test creating a service (non-stock) item"""
	# Load configuration
	with open('example_config.json', 'r') as f:
		config = json.load(f)

	# Initialize client
	client = ItemAPIClient(
		site_url=config['site_url'],
		api_key=config['api_key'],
		api_secret=config['api_secret']
	)

	print("\n" + "=" * 60)
	print("TEST 3: Creating Service Item (Non-Stock)")
	print("=" * 60)

	# Service item data
	item_data = {
		"item_code": "TEST-SERV-001",
		"item_name": "Consulting Service",
		"item_group": "Services",  # Update with your service group
		"description": "Professional consulting service",
		"stock_uom": "Hour",
		"is_stock_item": 0,
		"maintain_stock": 0,
		"standard_rate": 500.00,
		"company": "ZATCA Company",  # Update with your company
		"item_tax_template": "VAT 15 - GSS",  # Update with your tax template
		"tax_category": "VAT-GSS"  # Update with your tax category
	}

	# Create item
	print("\nCreating service item...")
	result = client.create_item(item_data)

	print("\nResponse:")
	print(json.dumps(result, indent=2))

	if result.get('success'):
		print(f"\n✓ Service item created successfully: {result.get('item_code')}")
		print(f"  URL: {result.get('item_url')}")
	else:
		print(f"\n✗ Failed to create service item: {result.get('message')}")

	return result


def test_create_multi_company_item():
	"""Test creating an item for multiple companies"""
	# Load configuration
	with open('example_config.json', 'r') as f:
		config = json.load(f)

	# Initialize client
	client = ItemAPIClient(
		site_url=config['site_url'],
		api_key=config['api_key'],
		api_secret=config['api_secret']
	)

	print("\n" + "=" * 60)
	print("TEST 4: Creating Multi-Company Item")
	print("=" * 60)

	# Multi-company item data
	item_data = {
		"item_code": "TEST-MULTI-001",
		"item_name": "Multi-Company Product",
		"item_group": "Products",
		"description": "Product available across multiple companies",
		"stock_uom": "Nos",
		"standard_rate": 200.00,
		"tax_templates": [
			{
				"item_tax_template": "VAT 15 - GSS",
				"tax_category": "VAT-GSS"
			}
		],
		"item_defaults": [
			{
				"company": "Company A",  # Update with your companies
				"default_warehouse": "Stores - CA",
				"default_price_list": "Standard Selling",
				"income_account": "Sales - CA",
				"expense_account": "Cost of Goods Sold - CA"
			},
			{
				"company": "Company B",  # Update with your companies
				"default_warehouse": "Stores - CB",
				"default_price_list": "Standard Selling",
				"income_account": "Sales - CB",
				"expense_account": "Cost of Goods Sold - CB"
			}
		]
	}

	# Create item
	print("\nCreating multi-company item...")
	result = client.create_item(item_data)

	print("\nResponse:")
	print(json.dumps(result, indent=2))

	if result.get('success'):
		print(f"\n✓ Multi-company item created successfully: {result.get('item_code')}")
		print(f"  URL: {result.get('item_url')}")
	else:
		print(f"\n✗ Failed to create multi-company item: {result.get('message')}")

	return result


if __name__ == "__main__":
	print("\n" + "=" * 60)
	print("ITEM API TEST CLIENT")
	print("=" * 60)

	# Note: Update the example_config.json file with your credentials before running

	# Uncomment the tests you want to run:

	# Get configuration data (run this first to see available options)
	# test_get_configuration()

	# Create basic item
	# test_create_basic_item()

	# Create item with VAT
	# test_create_vat_item()

	# Create service item
	# test_create_service_item()

	# Create multi-company item
	# test_create_multi_company_item()

	print("\n" + "=" * 60)
	print("Please update example_config.json with your credentials")
	print("and uncomment the test you want to run in the __main__ block")
	print("=" * 60)
