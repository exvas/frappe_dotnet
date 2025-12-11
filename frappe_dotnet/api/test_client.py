"""
Test client for Sales Invoice API
Run this script to test the API endpoints
"""

import requests
import json
from typing import Dict, Any


class SalesInvoiceAPIClient:
	"""Client for interacting with the Sales Invoice API"""

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

	def create_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Create a new Sales Invoice

		Args:
			invoice_data: Dictionary containing invoice details

		Returns:
			API response as dictionary
		"""
		url = f"{self.site_url}/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice"

		try:
			response = requests.post(url, json=invoice_data, headers=self.headers)
			response.raise_for_status()
			return response.json().get('message', {})
		except requests.exceptions.RequestException as e:
			print(f"Error creating invoice: {e}")
			if hasattr(e, 'response') and e.response is not None:
				return e.response.json()
			return {"success": False, "message": str(e)}

	def update_qr_code(self, invoice_name: str, qr_code: str) -> Dict[str, Any]:
		"""
		Update QR code for an existing invoice

		Args:
			invoice_name: Invoice ID
			qr_code: QR code data

		Returns:
			API response as dictionary
		"""
		url = f"{self.site_url}/api/method/frappe_dotnet.api.sales_invoice.update_invoice_qr_code"

		data = {
			"invoice_name": invoice_name,
			"qr_code": qr_code
		}

		try:
			response = requests.post(url, json=data, headers=self.headers)
			response.raise_for_status()
			return response.json().get('message', {})
		except requests.exceptions.RequestException as e:
			print(f"Error updating QR code: {e}")
			if hasattr(e, 'response') and e.response is not None:
				return e.response.json()
			return {"success": False, "message": str(e)}


def test_basic_invoice():
	"""Test creating a basic invoice"""
	# Load configuration
	with open('example_config.json', 'r') as f:
		config = json.load(f)

	# Initialize client
	client = SalesInvoiceAPIClient(
		site_url=config['site_url'],
		api_key=config['api_key'],
		api_secret=config['api_secret']
	)

	# Invoice data with complete customer and address details
	invoice_data = {
		"company": "Company A",  # Update with your company name
		"customer_name": "Test Customer Ltd",
		"customer_email": "test@example.com",
		"customer_phone": "+966501234567",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "All Territories",
		# Customer ZATCA fields
		"custom_vat_registration_number": "312038504300003",
		"commercial_registration_number": "1010394694",
		# Address details
		"address_line1": "King Fahd Road",
		"address_line2": "Building 123, Floor 4",
		"custom_building_number": "7890",
		"custom_area": "Al Olaya District",
		"city": "Riyadh",
		"state": "Riyadh Region",
		"pincode": "12345",
		"country": "Saudi Arabia",
		# Invoice items
		"items": [
			{
				"item_code": "ITEM-001",  # Update with your item code
				"qty": 10,
				"rate": 100.00,
				"description": "Test Item 1"
			},
			{
				"item_code": "ITEM-002",  # Update with your item code
				"qty": 5,
				"rate": 50.00,
				"discount_percentage": 10
			}
		],
		"qr_code": "ARVNVNLlE5BSkQgVFJBREVRyRBFU1QCD..."
	}

	# Create invoice
	print("Creating invoice...")
	result = client.create_invoice(invoice_data)

	print("\nResponse:")
	print(json.dumps(result, indent=2))

	if result.get('success'):
		print(f"\n✓ Invoice created successfully: {result.get('invoice_name')}")
		print(f"  URL: {result.get('invoice_url')}")
		print(f"  Grand Total: {result.get('grand_total')}")
	else:
		print(f"\n✗ Failed to create invoice: {result.get('message')}")

	return result


def test_update_qr_code():
	"""Test updating QR code for an existing invoice"""
	# Load configuration
	with open('example_config.json', 'r') as f:
		config = json.load(f)

	# Initialize client
	client = SalesInvoiceAPIClient(
		site_url=config['site_url'],
		api_key=config['api_key'],
		api_secret=config['api_secret']
	)

	# Update with an actual invoice name
	invoice_name = "SINV-2025-00001"
	qr_code = "NEW_QR_CODE_DATA_HERE..."

	print(f"Updating QR code for invoice {invoice_name}...")
	result = client.update_qr_code(invoice_name, qr_code)

	print("\nResponse:")
	print(json.dumps(result, indent=2))

	if result.get('success'):
		print(f"\n✓ QR code updated successfully")
	else:
		print(f"\n✗ Failed to update QR code: {result.get('message')}")


def test_error_handling():
	"""Test various error scenarios"""
	# Load configuration
	with open('example_config.json', 'r') as f:
		config = json.load(f)

	client = SalesInvoiceAPIClient(
		site_url=config['site_url'],
		api_key=config['api_key'],
		api_secret=config['api_secret']
	)

	print("Testing error scenarios...\n")

	# Test 1: Missing required fields
	print("1. Testing missing required fields...")
	result = client.create_invoice({"company": "Company A"})
	print(f"   Result: {result.get('message')}\n")

	# Test 2: Invalid company
	print("2. Testing invalid company...")
	result = client.create_invoice({
		"company": "Non Existent Company",
		"customer_name": "Test",
		"items": [{"item_code": "ITEM-001", "qty": 1}]
	})
	print(f"   Result: {result.get('message')}\n")

	# Test 3: Invalid item code
	print("3. Testing invalid item code...")
	result = client.create_invoice({
		"company": "Company A",
		"customer_name": "Test",
		"items": [{"item_code": "INVALID-ITEM", "qty": 1}]
	})
	print(f"   Result: {result.get('message')}\n")


if __name__ == "__main__":
	print("Sales Invoice API Test Client")
	print("=" * 50)

	# Update the example_config.json file with your credentials before running

	# Uncomment the test you want to run:

	# Test 1: Create a basic invoice
	# test_basic_invoice()

	# Test 2: Update QR code
	# test_update_qr_code()

	# Test 3: Test error handling
	# test_error_handling()

	print("\nPlease update example_config.json with your credentials")
	print("and uncomment the test you want to run in the __main__ block")
