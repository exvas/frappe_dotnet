# Item API Documentation

## Overview

This API enables external systems to create ERPNext Items with Item Tax Templates and Tax Categories. It supports company-specific tax configurations and item defaults.

## Features

- Create Items via API
- Configure Item Tax Templates per company
- Set Tax Categories (e.g., VAT-GSS)
- Company-specific item defaults
- Multi-company support
- API key-based authentication
- Comprehensive validation and error handling

---

## API Endpoints

### 1. Create Item

**Endpoint:** `/api/method/frappe_dotnet.api.item.create_item`

**Method:** `POST` or `GET`

**Description:** Creates a new Item with tax templates and company-specific settings.

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `item_code` | string | Unique item code |
| `item_name` | string | Item name/description |
| `item_group` | string | Item group (must exist in ERPNext) |

#### Optional Parameters

**Basic Item Details:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | string | item_name | Detailed description |
| `stock_uom` | string | "Nos" | Unit of measure |
| `is_stock_item` | int | 1 | Track stock (1=Yes, 0=No) |
| `maintain_stock` | int | 1 | Maintain stock (1=Yes, 0=No) |
| `standard_rate` | float | 0 | Standard selling rate |
| `valuation_rate` | float | 0 | Valuation rate |
| `opening_stock` | float | 0 | Opening stock quantity |

**Tax Configuration:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `company` | string | Company for single tax template |
| `item_tax_template` | string | Tax template name (e.g., "VAT 15 - GSS") |
| `tax_category` | string | Tax category (e.g., "VAT-GSS") |
| `tax_templates` | array | Multiple tax templates (see structure below) |

**Company Defaults:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `item_defaults` | array | Company-specific defaults (see structure below) |
| `default_warehouse` | string | Default warehouse for single company |
| `default_price_list` | string | Default price list |
| `expense_account` | string | Expense account |
| `income_account` | string | Income account |

#### Tax Templates Structure

For multiple tax templates:

```json
{
  "tax_templates": [
    {
      "item_tax_template": "VAT 15 - GSS",
      "tax_category": "VAT-GSS",
      "valid_from": "2025-01-01",
      "minimum_net_rate": 0,
      "maximum_net_rate": 0
    }
  ]
}
```

#### Item Defaults Structure

For multiple companies:

```json
{
  "item_defaults": [
    {
      "company": "Company A",
      "default_warehouse": "Stores - CA",
      "default_price_list": "Standard Selling",
      "expense_account": "Cost of Goods Sold - CA",
      "income_account": "Sales - CA"
    }
  ]
}
```

#### Response Format

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "message": "Item ITEM-001 created successfully",
    "item_code": "ITEM-001",
    "item_name": "Test Product",
    "item_url": "https://your-site.com/app/item/ITEM-001"
  }
}
```

**Error Response:**

```json
{
  "message": {
    "success": false,
    "message": "Item code 'ITEM-001' already exists",
    "item_code": null
  }
}
```

---

### 2. Get Tax Templates

**Endpoint:** `/api/method/frappe_dotnet.api.item.get_tax_templates`

**Method:** `GET` or `POST`

**Description:** Retrieves available Item Tax Templates, optionally filtered by company.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company` | string | No | Filter by company name |

#### Response

```json
{
  "message": {
    "success": true,
    "tax_templates": [
      {
        "name": "VAT 15 - GSS",
        "title": "VAT 15%",
        "company": "ZATCA Company"
      }
    ]
  }
}
```

---

### 3. Get Tax Categories

**Endpoint:** `/api/method/frappe_dotnet.api.item.get_tax_categories`

**Method:** `GET` or `POST`

**Description:** Retrieves available Tax Categories.

#### Response

```json
{
  "message": {
    "success": true,
    "tax_categories": [
      {
        "name": "VAT-GSS",
        "title": "VAT GSS",
        "disabled": 0
      }
    ]
  }
}
```

---

### 4. Get Item Groups

**Endpoint:** `/api/method/frappe_dotnet.api.item.get_item_groups`

**Method:** `GET` or `POST`

**Description:** Retrieves available Item Groups.

#### Response

```json
{
  "message": {
    "success": true,
    "item_groups": [
      {
        "name": "Products",
        "parent_item_group": "All Item Groups",
        "is_group": 0
      }
    ]
  }
}
```

---

## Example Requests

### Example 1: Basic Item (cURL)

```bash
curl -X POST https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.item.create_item \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "item_code": "PROD-001",
    "item_name": "Test Product",
    "item_group": "Products",
    "description": "Test product for demonstration",
    "stock_uom": "Nos",
    "standard_rate": 100
  }'
```

### Example 2: Item with Tax Template and Category (cURL)

```bash
curl -X POST https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.item.create_item \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "item_code": "PROD-002",
    "item_name": "VAT Product",
    "item_group": "Products",
    "company": "ZATCA Company",
    "item_tax_template": "VAT 15 - GSS",
    "tax_category": "VAT-GSS",
    "standard_rate": 150,
    "default_warehouse": "Stores - ZATCA"
  }'
```

### Example 3: Complete Item with Multiple Tax Templates (Python)

```python
import requests

url = "https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.item.create_item"

headers = {
    "Authorization": "token YOUR_KEY:YOUR_SECRET",
    "Content-Type": "application/json"
}

payload = {
    "item_code": "PROD-003",
    "item_name": "Premium Product",
    "item_group": "Products",
    "description": "Premium product with VAT",
    "stock_uom": "Nos",
    "standard_rate": 500,
    "valuation_rate": 400,
    "is_stock_item": 1,
    "maintain_stock": 1,
    "tax_templates": [
        {
            "item_tax_template": "VAT 15 - GSS",
            "tax_category": "VAT-GSS"
        }
    ],
    "item_defaults": [
        {
            "company": "ZATCA Company",
            "default_warehouse": "Stores - ZATCA",
            "default_price_list": "Standard Selling",
            "income_account": "Sales - ZATCA",
            "expense_account": "Cost of Goods Sold - ZATCA"
        }
    ]
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### Example 4: JavaScript/Node.js

```javascript
const axios = require('axios');

const createItem = async () => {
  try {
    const response = await axios.post(
      'https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.item.create_item',
      {
        item_code: 'PROD-004',
        item_name: 'Service Item',
        item_group: 'Services',
        is_stock_item: 0,
        maintain_stock: 0,
        company: 'ZATCA Company',
        item_tax_template: 'VAT 15 - GSS',
        tax_category: 'VAT-GSS',
        standard_rate: 1000
      },
      {
        headers: {
          'Authorization': 'token YOUR_KEY:YOUR_SECRET',
          'Content-Type': 'application/json'
        }
      }
    );

    console.log('Item created:', response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
};

createItem();
```

### Example 5: C#/.NET

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class ItemCreator
{
    private static readonly HttpClient client = new HttpClient();

    public static async Task CreateItem()
    {
        var url = "https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.item.create_item";

        var itemData = new
        {
            item_code = "PROD-005",
            item_name = "DotNet Product",
            item_group = "Products",
            company = "ZATCA Company",
            item_tax_template = "VAT 15 - GSS",
            tax_category = "VAT-GSS",
            standard_rate = 250,
            stock_uom = "Nos"
        };

        var json = JsonSerializer.Serialize(itemData);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        client.DefaultRequestHeaders.Add("Authorization", "token YOUR_KEY:YOUR_SECRET");

        try
        {
            var response = await client.PostAsync(url, content);
            var result = await response.Content.ReadAsStringAsync();
            Console.WriteLine(result);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
```

### Example 6: Get Tax Templates (Python)

```python
import requests

url = "https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.item.get_tax_templates"

headers = {
    "Authorization": "token YOUR_KEY:YOUR_SECRET"
}

params = {
    "company": "ZATCA Company"
}

response = requests.get(url, headers=headers, params=params)
templates = response.json()["message"]["tax_templates"]

for template in templates:
    print(f"{template['name']} - {template['company']}")
```

---

## Workflow: Creating Item with Proper Tax Configuration

### Step 1: Get Available Tax Templates

```bash
curl -X GET "https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.item.get_tax_templates?company=ZATCA%20Company" \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET"
```

### Step 2: Get Available Tax Categories

```bash
curl -X GET https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.item.get_tax_categories \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET"
```

### Step 3: Get Available Item Groups

```bash
curl -X GET https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.item.get_item_groups \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET"
```

### Step 4: Create Item with Selected Configuration

```bash
curl -X POST https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.item.create_item \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "item_code": "PROD-NEW",
    "item_name": "New Product",
    "item_group": "Products",
    "company": "ZATCA Company",
    "item_tax_template": "VAT 15 - GSS",
    "tax_category": "VAT-GSS",
    "standard_rate": 100
  }'
```

---

## Common Use Cases

### Use Case 1: Simple Product Item

```json
{
  "item_code": "PROD-SIMPLE-001",
  "item_name": "Simple Product",
  "item_group": "Products",
  "stock_uom": "Nos",
  "standard_rate": 50
}
```

### Use Case 2: VAT-Enabled Product

```json
{
  "item_code": "PROD-VAT-001",
  "item_name": "VAT Product",
  "item_group": "Products",
  "company": "ZATCA Company",
  "item_tax_template": "VAT 15 - GSS",
  "tax_category": "VAT-GSS",
  "standard_rate": 100,
  "default_warehouse": "Stores - ZATCA"
}
```

### Use Case 3: Service Item (Non-Stock)

```json
{
  "item_code": "SERV-001",
  "item_name": "Consulting Service",
  "item_group": "Services",
  "is_stock_item": 0,
  "maintain_stock": 0,
  "stock_uom": "Hour",
  "company": "ZATCA Company",
  "item_tax_template": "VAT 15 - GSS",
  "tax_category": "VAT-GSS",
  "standard_rate": 500
}
```

### Use Case 4: Multi-Company Item

```json
{
  "item_code": "PROD-MULTI-001",
  "item_name": "Multi-Company Product",
  "item_group": "Products",
  "standard_rate": 200,
  "tax_templates": [
    {
      "item_tax_template": "VAT 15 - GSS",
      "tax_category": "VAT-GSS"
    }
  ],
  "item_defaults": [
    {
      "company": "Company A",
      "default_warehouse": "Stores - CA",
      "income_account": "Sales - CA"
    },
    {
      "company": "Company B",
      "default_warehouse": "Stores - CB",
      "income_account": "Sales - CB"
    }
  ]
}
```

---

## Error Handling

### Common Error Types

| Error Type | Description |
|------------|-------------|
| Authentication Error | Invalid or missing API credentials |
| Permission Error | User lacks permission to create items |
| Validation Error | Invalid data (missing fields, wrong format) |
| Duplicate Entry Error | Item code already exists |
| Does Not Exist Error | Referenced item group/tax template doesn't exist |

### Error Message Examples

```json
{
  "success": false,
  "message": "Missing required fields: item_code, item_name"
}
```

```json
{
  "success": false,
  "message": "Item code 'PROD-001' already exists"
}
```

```json
{
  "success": false,
  "message": "Item Group 'Invalid Group' does not exist. Please check the item group."
}
```

```json
{
  "success": false,
  "message": "Item Tax Template 'VAT 20 - GSS' does not exist"
}
```

---

## Best Practices

1. **Always Check for Duplicates:** Query existing items before creation

2. **Validate Tax Templates:** Use `get_tax_templates` to verify template names

3. **Validate Tax Categories:** Use `get_tax_categories` to verify category names

4. **Validate Item Groups:** Use `get_item_groups` to verify group names

5. **Use Appropriate UOM:** Ensure the UOM exists in ERPNext

6. **Set Proper Rates:** Provide standard_rate for selling items

7. **Configure Company Defaults:** Set default warehouse and accounts for each company

8. **Handle Non-Stock Items:** Set `is_stock_item: 0` for service items

9. **Test First:** Create test items in a development environment

10. **Monitor Responses:** Log API responses for debugging

---

## Integration Example

Complete workflow for creating items from an external system:

```python
import requests

class ItemManager:
    def __init__(self, base_url, api_key, api_secret):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"token {api_key}:{api_secret}",
            "Content-Type": "application/json"
        }

    def get_tax_templates(self, company):
        """Get available tax templates for a company"""
        url = f"{self.base_url}/api/method/frappe_dotnet.api.item.get_tax_templates"
        response = requests.get(url, headers=self.headers, params={"company": company})
        return response.json()["message"]["tax_templates"]

    def get_tax_categories(self):
        """Get available tax categories"""
        url = f"{self.base_url}/api/method/frappe_dotnet.api.item.get_tax_categories"
        response = requests.get(url, headers=self.headers)
        return response.json()["message"]["tax_categories"]

    def create_item(self, item_data):
        """Create an item"""
        url = f"{self.base_url}/api/method/frappe_dotnet.api.item.create_item"
        response = requests.post(url, headers=self.headers, json=item_data)
        return response.json()["message"]

# Usage
manager = ItemManager(
    "https://techbrightsolutions.saas-erp.in",
    "YOUR_API_KEY",
    "YOUR_API_SECRET"
)

# Get tax templates
templates = manager.get_tax_templates("ZATCA Company")
print("Available templates:", [t["name"] for t in templates])

# Create item with VAT
result = manager.create_item({
    "item_code": "PROD-API-001",
    "item_name": "API Created Product",
    "item_group": "Products",
    "company": "ZATCA Company",
    "item_tax_template": "VAT 15 - GSS",
    "tax_category": "VAT-GSS",
    "standard_rate": 100
})

print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
if result['success']:
    print(f"Item URL: {result['item_url']}")
```

---

## Troubleshooting

### Issue: "Item Tax Template does not exist"

**Solution:** Use `get_tax_templates` to get the exact template name including company abbreviation

### Issue: "Tax Category does not exist"

**Solution:** Create the tax category in ERPNext first, or use `get_tax_categories` to verify names

### Issue: "Item Group does not exist"

**Solution:** Use `get_item_groups` to get valid item group names

### Issue: "Item code already exists"

**Solution:** Each item code must be unique. Check existing items before creating new ones

---

## Quick Reference

**Base URL:** `https://techbrightsolutions.saas-erp.in`

**Endpoints:**
- Create Item: `/api/method/frappe_dotnet.api.item.create_item`
- Get Tax Templates: `/api/method/frappe_dotnet.api.item.get_tax_templates`
- Get Tax Categories: `/api/method/frappe_dotnet.api.item.get_tax_categories`
- Get Item Groups: `/api/method/frappe_dotnet.api.item.get_item_groups`

**Required Fields:**
- `item_code`
- `item_name`
- `item_group`

**Key Optional Fields:**
- `company` + `item_tax_template` + `tax_category` (for VAT items)
- `standard_rate` (selling price)
- `is_stock_item` (0 for services)

---

**Version:** 1.0.0
**Last Updated:** 2025-12-11
