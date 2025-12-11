# Sales Invoice API Documentation

## Overview

This API enables external systems to create ERPNext Sales Invoices with automatic customer creation and ZATCA-compliant QR code management. It supports multi-company configurations and provides comprehensive error handling with user-friendly messages.

## Features

- Create Sales Invoices via API
- Automatic customer creation if customer doesn't exist
- Multi-company support
- ZATCA QR code integration
- API key-based authentication
- Comprehensive validation and error handling
- Transaction rollback on failures

---

## Authentication

All API endpoints require authentication using Frappe API keys.

### Generating API Keys

1. Login to your ERPNext instance
2. Go to **User** > Select your user
3. Click on **API Access** section
4. Generate **API Key** and **API Secret**
5. Save both securely

### Authentication Methods

#### Option 1: HTTP Headers (Recommended)

```bash
Authorization: token <api_key>:<api_secret>
```

#### Option 2: Query Parameters

```bash
?api_key=<api_key>&api_secret=<api_secret>
```

---

## API Endpoints

### 1. Create Sales Invoice

**Endpoint:** `/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice`

**Method:** `POST` or `GET`

**Description:** Creates a new Sales Invoice. If the customer doesn't exist, it will be created automatically.

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `company` | string | Company name (must exist in ERPNext) |
| `customer_name` | string | Customer name (will be created if doesn't exist) |
| `items` | array | List of invoice items (see Items Structure below) |

#### Optional Parameters

**Customer Details:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `customer_email` | string | - | Customer email address |
| `customer_phone` | string | - | Customer mobile number |
| `customer_group` | string | "Commercial" | Customer group |
| `customer_type` | string | "Company" | Customer type (Company/Individual) |
| `territory` | string | "All Territories" | Territory |
| `custom_vat_registration_number` | string | - | VAT registration number (e.g., 312038504300003) |
| `commercial_registration_number` | string | - | Commercial registration number (CRN) |

**Address Details (for new customers):**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `address_line1` | string | - | Primary address line |
| `address_line2` | string | - | Secondary address line |
| `custom_building_number` | string | - | Building number (ZATCA required) |
| `custom_area` | string | - | Area/District (ZATCA required) |
| `city` | string | - | City name |
| `county` | string | - | County |
| `state` | string | - | State/Province |
| `pincode` | string | - | Postal/ZIP code |
| `country` | string | "Saudi Arabia" | Country name |

**Invoice Details:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `posting_date` | date | Today | Invoice posting date (YYYY-MM-DD) |
| `due_date` | date | - | Payment due date (YYYY-MM-DD) |
| `currency` | string | Company default | Currency code (e.g., SAR, USD) |
| `qr_code` | string | - | ZATCA QR code data |
| `submit_invoice` | boolean | false | Auto-submit invoice after creation |
| `additional_fields` | object | - | Custom field values (key-value pairs) |

#### Items Structure

Each item in the `items` array should have:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `item_code` | string | Yes | Item code (must exist in ERPNext) |
| `qty` | float | Yes | Quantity |
| `rate` | float | No | Unit price (uses item default if not provided) |
| `uom` | string | No | Unit of measure (uses item default) |
| `warehouse` | string | No | Warehouse (uses company default) |
| `description` | string | No | Item description |
| `discount_percentage` | float | No | Discount percentage (0-100) |
| `income_account` | string | No | Income account |
| `cost_center` | string | No | Cost center |

#### Response Format

**Success Response (200 OK):**

```json
{
  "success": true,
  "message": "Sales Invoice SINV-2025-00001 created successfully",
  "invoice_name": "SINV-2025-00001",
  "invoice_url": "https://your-site.com/app/sales-invoice/SINV-2025-00001",
  "customer": "Customer Name",
  "grand_total": 1150.00
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Validation Error: Item 'ITEM-001' does not exist in the system",
  "invoice_name": null
}
```

#### Example Requests

##### Example 1: Complete Invoice with Customer Address (cURL)

```bash
curl -X POST https://your-site.com/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice \
  -H "Authorization: token abc123:xyz789" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "ZATCA Company",
    "customer_name": "Al Khamis Al Arabiya Trading Company",
    "customer_email": "info@alkhamis.com",
    "customer_phone": "+966501234567",
    "customer_type": "Company",
    "customer_group": "Commercial",
    "custom_vat_registration_number": "312038504300003",
    "commercial_registration_number": "1010394694",
    "address_line1": "King Fahd Road",
    "address_line2": "Building 123, Floor 4",
    "custom_building_number": "7890",
    "custom_area": "Al Olaya District",
    "city": "Riyadh",
    "state": "Riyadh Region",
    "pincode": "12345",
    "country": "Saudi Arabia",
    "items": [
      {
        "item_code": "ITEM-001",
        "qty": 10,
        "rate": 100
      },
      {
        "item_code": "ITEM-002",
        "qty": 5,
        "rate": 50,
        "discount_percentage": 10
      }
    ],
    "qr_code": "ARVNVNLlE5BSkQgVFJBREVRyRBFU1QCD..."
  }'
```

##### Example 2: Multi-Company with Custom Fields (Python)

```python
import requests

url = "https://your-site.com/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice"

headers = {
    "Authorization": "token abc123:xyz789",
    "Content-Type": "application/json"
}

payload = {
    "company": "Company A",
    "customer_name": "New Customer Ltd",
    "customer_type": "Company",
    "customer_group": "Commercial",
    "territory": "Saudi Arabia",
    "customer_email": "contact@newcustomer.com",
    "customer_phone": "+966555123456",
    "custom_vat_registration_number": "300000000000003",
    "commercial_registration_number": "2020123456",
    "address_line1": "Prince Sultan Street",
    "address_line2": "Office 201",
    "custom_building_number": "4567",
    "custom_area": "Al Malaz",
    "city": "Riyadh",
    "state": "Riyadh Region",
    "pincode": "11564",
    "country": "Saudi Arabia",
    "posting_date": "2025-12-11",
    "due_date": "2025-12-31",
    "items": [
        {
            "item_code": "SERVICE-001",
            "qty": 1,
            "rate": 5000,
            "description": "Consulting Services"
        }
    ],
    "qr_code": "ARVNVNLlE5BSkQgVFJBREVRyRBFU1Q...",
    "submit_invoice": True,
    "additional_fields": {
        "custom_reference": "REF-2025-001",
        "custom_notes": "Payment via bank transfer"
    }
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

##### Example 3: JavaScript/Node.js

```javascript
const axios = require('axios');

const createInvoice = async () => {
  try {
    const response = await axios.post(
      'https://your-site.com/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice',
      {
        company: 'ZATCA Company',
        customer_name: 'XYZ Corporation',
        customer_email: 'contact@xyzcorp.com',
        items: [
          {
            item_code: 'PROD-001',
            qty: 20,
            rate: 75.50
          }
        ],
        qr_code: 'ARVNVNLlE5BSkQgVFJBREVRyRBFU1Q...'
      },
      {
        headers: {
          'Authorization': 'token abc123:xyz789',
          'Content-Type': 'application/json'
        }
      }
    );

    console.log('Invoice created:', response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
};

createInvoice();
```

##### Example 4: C#/.NET

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class InvoiceCreator
{
    private static readonly HttpClient client = new HttpClient();

    public static async Task CreateInvoice()
    {
        var url = "https://your-site.com/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice";

        var invoiceData = new
        {
            company = "ZATCA Company",
            customer_name = "Test Customer",
            customer_email = "test@example.com",
            items = new[]
            {
                new
                {
                    item_code = "ITEM-001",
                    qty = 5,
                    rate = 100.00
                }
            },
            qr_code = "ARVNVNLlE5BSkQgVFJBREVRyRBFU1Q..."
        };

        var json = JsonSerializer.Serialize(invoiceData);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        client.DefaultRequestHeaders.Add("Authorization", "token abc123:xyz789");

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

---

### 2. Update Invoice QR Code

**Endpoint:** `/api/method/frappe_dotnet.api.sales_invoice.update_invoice_qr_code`

**Method:** `POST` or `GET`

**Description:** Updates the QR code for an existing Sales Invoice.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `invoice_name` | string | Yes | Sales Invoice ID (e.g., SINV-2025-00001) |
| `qr_code` | string | Yes | ZATCA QR code data |

#### Response Format

**Success Response:**

```json
{
  "success": true,
  "message": "QR Code updated successfully for invoice SINV-2025-00001"
}
```

**Error Response:**

```json
{
  "success": false,
  "message": "Sales Invoice 'SINV-2025-00001' does not exist"
}
```

#### Example Request (cURL)

```bash
curl -X POST https://your-site.com/api/method/frappe_dotnet.api.sales_invoice.update_invoice_qr_code \
  -H "Authorization: token abc123:xyz789" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_name": "SINV-2025-00001",
    "qr_code": "ARVNVNLlE5BSkQgVFJBREVRyRBFU1QCD..."
  }'
```

---

## Customer Creation

### Automatic Customer Creation

When you create a Sales Invoice, if the customer doesn't exist, it will be automatically created with all provided details:

**What Gets Created:**

1. **Customer Record** with:
   - Customer name
   - Email and phone
   - Customer type, group, and territory
   - VAT registration number (custom field: `custom_vat_registration_number`)
   - Commercial registration number (added to `custom_additional_ids` child table)

2. **Customer Address** (if address fields provided):
   - Address linked to the customer
   - Includes all standard and custom address fields
   - Address type set to "Billing"

**Custom Fields Required:**

Before using the API, ensure these custom fields exist in your ERPNext:

**Customer DocType:**
- Field: `custom_vat_registration_number` (Data or Small Text)
- Field: `custom_additional_ids` (Table with columns: type_name, type_code, value)

**Address DocType:**
- Field: `custom_building_number` (Data)
- Field: `custom_area` (Data)

### Example Customer Creation Flow

```python
# When this invoice is created for a new customer:
payload = {
    "company": "ZATCA Company",
    "customer_name": "Al Khamis Al Arabiya Trading Company",
    "custom_vat_registration_number": "312038504300003",
    "commercial_registration_number": "1010394694",
    "address_line1": "King Fahd Road",
    "custom_building_number": "7890",
    "custom_area": "Al Olaya District",
    "city": "Riyadh",
    # ... other fields
}

# The API will:
# 1. Check if customer "Al Khamis Al Arabiya Trading Company" exists
# 2. If not, create new customer with:
#    - customer_name: "Al Khamis Al Arabiya Trading Company"
#    - custom_vat_registration_number: "312038504300003"
#    - custom_additional_ids row: type_name="Commercial Registration Number", value="1010394694"
# 3. Create address linked to customer with building number and area
# 4. Create sales invoice using the customer
```

### Existing Customer Behavior

If the customer already exists (matched by `customer_name`):
- The existing customer is used
- Address and custom fields are **NOT** updated
- Only the invoice is created

To update existing customer details, use ERPNext's standard Customer API or UI.

---

## Error Handling

The API provides user-friendly error messages for common scenarios:

### Common Error Types

| Error Type | HTTP Status | Description |
|------------|-------------|-------------|
| Authentication Error | 401 | Invalid or missing API credentials |
| Permission Error | 403 | User lacks permission to create invoices |
| Validation Error | 417 | Invalid data (missing fields, wrong format) |
| Does Not Exist Error | 404 | Referenced item/company doesn't exist |
| Server Error | 500 | Unexpected server error |

### Error Message Examples

```json
{
  "success": false,
  "message": "Missing required fields: company, items"
}
```

```json
{
  "success": false,
  "message": "Company 'XYZ Corp' does not exist. Please check the company name."
}
```

```json
{
  "success": false,
  "message": "Item 'PROD-999' does not exist in the system"
}
```

```json
{
  "success": false,
  "message": "Permission Denied: You don't have permission to create invoices for this company"
}
```

---

## Multi-Company Setup

### Configuration Steps

1. **Create Companies in ERPNext:**
   - Go to: **Setup > Company**
   - Create multiple companies as needed

2. **Create API Users per Company:**
   - Create separate users for each company
   - Assign appropriate roles (Sales Invoice Manager, Sales User)
   - Generate API keys for each user

3. **Set Company Permissions:**
   - Go to: **User > Role Permissions Manager**
   - Configure company-wise permissions

4. **Use Company-Specific API Keys:**
   - Each API request should use credentials with access to the target company
   - The `company` parameter must match the company the API user has access to

### Example Multi-Company Request

```python
# Company A Invoice
response_a = requests.post(
    url,
    json={"company": "Company A", ...},
    headers={"Authorization": "token company_a_key:company_a_secret"}
)

# Company B Invoice
response_b = requests.post(
    url,
    json={"company": "Company B", ...},
    headers={"Authorization": "token company_b_key:company_b_secret"}
)
```

---

## ZATCA QR Code Integration

### QR Code Field Setup

Before using QR code functionality, ensure the custom field exists:

1. Go to: **Customize Form > Sales Invoice**
2. Add a new field:
   - **Label:** QR Code
   - **Fieldname:** `qr_code`
   - **Field Type:** Long Text or Data
3. Save

### QR Code Format

The QR code should be in ZATCA's base64-encoded format containing:
- Seller name
- VAT registration number
- Invoice timestamp
- Invoice total
- VAT amount

Example QR code structure:
```
ARVNVNLlE5BSkQgVFJBREVRyRBFU1QCD...
```

---

## Testing the API

### Using Postman

1. **Import Collection:**
   - Create a new request
   - Set method to POST
   - URL: `https://your-site.com/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice`

2. **Configure Authorization:**
   - Go to Authorization tab
   - Type: No Auth (we'll use headers)
   - Add header: `Authorization: token <your_key>:<your_secret>`

3. **Set Request Body:**
   - Select Body > raw > JSON
   - Paste your JSON payload

4. **Send Request**

### Test Checklist

- [ ] Create invoice with existing customer
- [ ] Create invoice with new customer (auto-creation)
- [ ] Create invoice with multiple items
- [ ] Create invoice with QR code
- [ ] Update QR code for existing invoice
- [ ] Test with invalid company name
- [ ] Test with non-existent item code
- [ ] Test with missing required fields
- [ ] Test with invalid API credentials
- [ ] Test multi-company access

---

## Troubleshooting

### Issue: "Authentication required"

**Solution:** Ensure you're passing valid API key and secret in the Authorization header.

```bash
Authorization: token <api_key>:<api_secret>
```

### Issue: "Company does not exist"

**Solution:** Verify the company name exactly matches the name in ERPNext (case-sensitive).

### Issue: "Item does not exist"

**Solution:** Check that all `item_code` values exist in the Item master. Go to **Stock > Item** to verify.

### Issue: "Permission Denied"

**Solution:** Ensure the API user has the following roles:
- Sales User
- Sales Invoice Manager (for submitting)
- Accounts User

### Issue: "QR Code field does not exist"

**Solution:** Create the custom field in Sales Invoice doctype (see ZATCA QR Code Integration section).

### Issue: Customer created but invoice failed

**Solution:** The API uses database transactions. If invoice creation fails, the customer creation is also rolled back. Check error logs:

```python
# In ERPNext
Error Log > Filter by title: "Sales Invoice Creation Failed"
```

---

## Best Practices

1. **Always validate data before sending:** Check that companies, items, and customers exist when possible

2. **Handle errors gracefully:** Parse the `success` field and display appropriate messages to users

3. **Use appropriate item rates:** Provide `rate` for each item to avoid using default prices

4. **Test with draft invoices first:** Don't set `submit_invoice: true` until you're confident in your integration

5. **Log API responses:** Keep audit trails of all API calls for troubleshooting

6. **Use HTTPS:** Never send API credentials over unencrypted connections

7. **Rotate API keys regularly:** Update keys periodically for security

8. **Implement retry logic:** Handle network failures with exponential backoff

9. **Validate QR codes:** Ensure QR code data is properly formatted before sending

10. **Monitor rate limits:** Frappe has built-in rate limiting; implement proper throttling

---

## Security Considerations

1. **Protect API Credentials:**
   - Never commit API keys to version control
   - Use environment variables or secure vaults
   - Rotate keys regularly

2. **IP Whitelisting:**
   - Configure ERPNext to accept API calls only from trusted IPs
   - Go to: **System Settings > API Access**

3. **HTTPS Only:**
   - Always use HTTPS endpoints
   - Validate SSL certificates

4. **Least Privilege:**
   - Create API users with minimum required permissions
   - Don't use Administrator accounts for API access

5. **Audit Logging:**
   - Monitor API access logs
   - Set up alerts for suspicious activity

---

## Support

For issues or questions:

1. Check the error message returned by the API
2. Review ERPNext Error Logs: **Setup > Error Log**
3. Check application logs: `bench --site <site-name> logs`
4. Contact your ERPNext administrator

---

## Changelog

### Version 1.0.0 (2025-12-11)
- Initial release
- Create Sales Invoice API
- Automatic customer creation
- Multi-company support
- ZATCA QR code integration
- Comprehensive error handling
