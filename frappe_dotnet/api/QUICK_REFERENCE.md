# Quick Reference - Sales Invoice API

## Base URL
```
https://techbrightsolutions.saas-erp.in
```

## Authentication
```
Authorization: token YOUR_API_KEY:YOUR_API_SECRET
```

---

## API Endpoints

### 1. Create Sales Invoice
```
POST /api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice
```

### 2. Update QR Code
```
POST /api/method/frappe_dotnet.api.sales_invoice.update_invoice_qr_code
```

---

## Minimal Request (cURL)

```bash
curl -X POST https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Your Company",
    "customer_name": "Test Customer",
    "items": [{"item_code": "ITEM-001", "qty": 1, "rate": 100}]
  }'
```

---

## Complete Request (cURL)

```bash
curl -X POST https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "ZATCA Company",
    "customer_name": "Al Khamis Al Arabiya Trading Company",
    "customer_email": "info@alkhamis.com",
    "customer_phone": "+966501234567",
    "custom_vat_registration_number": "312038504300003",
    "commercial_registration_number": "1010394694",
    "address_line1": "King Fahd Road",
    "custom_building_number": "7890",
    "custom_area": "Al Olaya District",
    "city": "Riyadh",
    "state": "Riyadh Region",
    "pincode": "12345",
    "country": "Saudi Arabia",
    "items": [
      {"item_code": "ITEM-001", "qty": 10, "rate": 100},
      {"item_code": "ITEM-002", "qty": 5, "rate": 50, "discount_percentage": 10}
    ],
    "qr_code": "YOUR_QR_CODE_DATA"
  }'
```

---

## Python Example

```python
import requests

url = "https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice"
headers = {
    "Authorization": "token YOUR_KEY:YOUR_SECRET",
    "Content-Type": "application/json"
}

payload = {
    "company": "Your Company",
    "customer_name": "Test Customer",
    "custom_vat_registration_number": "312038504300003",
    "items": [
        {"item_code": "ITEM-001", "qty": 10, "rate": 100}
    ]
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

---

## JavaScript Example

```javascript
const axios = require('axios');

axios.post(
  'https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice',
  {
    company: "Your Company",
    customer_name: "Test Customer",
    items: [
      { item_code: "ITEM-001", qty: 10, rate: 100 }
    ]
  },
  {
    headers: {
      'Authorization': 'token YOUR_KEY:YOUR_SECRET',
      'Content-Type': 'application/json'
    }
  }
)
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

---

## C# Example

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

var client = new HttpClient();
var url = "https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice";

var data = new {
    company = "Your Company",
    customer_name = "Test Customer",
    items = new[] {
        new { item_code = "ITEM-001", qty = 10, rate = 100 }
    }
};

var json = JsonSerializer.Serialize(data);
var content = new StringContent(json, Encoding.UTF8, "application/json");
client.DefaultRequestHeaders.Add("Authorization", "token YOUR_KEY:YOUR_SECRET");

var response = await client.PostAsync(url, content);
var result = await response.Content.ReadAsStringAsync();
Console.WriteLine(result);
```

---

## Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `company` | string | Company name (must exist) |
| `customer_name` | string | Customer name |
| `items` | array | Invoice items |
| `items[].item_code` | string | Item code (must exist) |
| `items[].qty` | number | Quantity |

---

## Customer Fields (Optional)

| Parameter | Description |
|-----------|-------------|
| `customer_email` | Email address |
| `customer_phone` | Phone number |
| `custom_vat_registration_number` | VAT number (e.g., 312038504300003) |
| `commercial_registration_number` | CRN (e.g., 1010394694) |

---

## Address Fields (Optional)

| Parameter | Description |
|-----------|-------------|
| `address_line1` | Primary address |
| `address_line2` | Secondary address |
| `custom_building_number` | Building number (ZATCA) |
| `custom_area` | Area/District (ZATCA) |
| `city` | City name |
| `state` | State/Province |
| `pincode` | Postal code |
| `country` | Country (default: Saudi Arabia) |

---

## Response Format

**Success:**
```json
{
  "message": {
    "success": true,
    "message": "Sales Invoice SINV-2025-00001 created successfully",
    "invoice_name": "SINV-2025-00001",
    "invoice_url": "https://techbrightsolutions.saas-erp.in/app/sales-invoice/SINV-2025-00001",
    "customer": "Customer Name",
    "grand_total": 1150.0
  }
}
```

**Error:**
```json
{
  "message": {
    "success": false,
    "message": "Error description here",
    "invoice_name": null
  }
}
```

---

## Common Errors

| Error | Solution |
|-------|----------|
| "Authentication required" | Check API key/secret |
| "Company does not exist" | Verify company name (case-sensitive) |
| "Item does not exist" | Check item code exists in ERPNext |
| "Permission Denied" | Assign proper roles to API user |

---

## Required Custom Fields

**Customer:**
- `custom_vat_registration_number` (Data)
- `custom_additional_ids` (Table: type_name, type_code, value)

**Address:**
- `custom_building_number` (Data)
- `custom_area` (Data)

**Sales Invoice:**
- `qr_code` (Long Text)

**Setup Script:** See [SETUP_GUIDE.md](../../SETUP_GUIDE.md) Step 2

---

## Test Authentication

```bash
curl -X GET https://techbrightsolutions.saas-erp.in/api/method/frappe.auth.get_logged_user \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET"
```

Expected: `{"message": "your-email@example.com"}`

---

## Update QR Code

```bash
curl -X POST https://techbrightsolutions.saas-erp.in/api/method/frappe_dotnet.api.sales_invoice.update_invoice_qr_code \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_name": "SINV-2025-00001",
    "qr_code": "YOUR_QR_CODE_DATA"
  }'
```

---

## Files Location

```
frappe_dotnet/api/
├── sales_invoice.py          # Main API implementation
├── README.md                  # Complete documentation
├── POSTMAN_SETUP.md          # Postman setup guide
├── QUICK_REFERENCE.md        # This file
├── Postman_Collection.json   # Import into Postman
├── test_client.py            # Python test client
└── example_config.json       # Configuration template
```

---

## Quick Links

- **Full Documentation:** [README.md](README.md)
- **Setup Guide:** [SETUP_GUIDE.md](../../SETUP_GUIDE.md)
- **Postman Guide:** [POSTMAN_SETUP.md](POSTMAN_SETUP.md)
- **ERPNext Site:** https://techbrightsolutions.saas-erp.in

---

**Version:** 1.0.0
**Last Updated:** 2025-12-11
