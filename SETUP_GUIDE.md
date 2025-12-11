# Sales Invoice API Setup Guide

## Quick Start

This guide will help you set up and use the Sales Invoice API for ERPNext integration.

---

## Prerequisites

- ERPNext installed and running
- Frappe bench setup
- Admin access to ERPNext
- Python 3.10+ (for testing scripts)

---

## Installation Steps

### 1. Install the App

```bash
# Navigate to your bench directory
cd ~/frappe-bench

# Install the app (if not already installed)
bench get-app https://github.com/your-username/frappe_dotnet.git

# Install app to your site
bench --site your-site-name install-app frappe_dotnet

# Restart bench
bench restart
```

### 2. Create Custom Fields (Required for ZATCA Compliance)

The API requires several custom fields for proper customer and invoice management. You can create them via UI or Console.

#### Option A: Via Console (Recommended - Creates All Fields at Once)

```bash
bench --site your-site-name console
```

```python
import frappe

# Custom Fields Configuration
custom_fields = {
    "Customer": [
        {
            "label": "VAT Registration Number",
            "fieldname": "custom_vat_registration_number",
            "fieldtype": "Data",
            "insert_after": "tax_id"
        },
        {
            "label": "Additional IDs",
            "fieldname": "custom_additional_ids",
            "fieldtype": "Table",
            "options": "Customer Additional ID",  # Child table
            "insert_after": "custom_vat_registration_number"
        }
    ],
    "Address": [
        {
            "label": "Building Number",
            "fieldname": "custom_building_number",
            "fieldtype": "Data",
            "insert_after": "address_line2"
        },
        {
            "label": "Area",
            "fieldname": "custom_area",
            "fieldtype": "Data",
            "insert_after": "custom_building_number"
        }
    ],
    "Sales Invoice": [
        {
            "label": "QR Code",
            "fieldname": "qr_code",
            "fieldtype": "Long Text",
            "insert_after": "customer"
        }
    ]
}

# Create custom fields
for doctype, fields in custom_fields.items():
    for field in fields:
        if not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": field["fieldname"]}):
            frappe.get_doc({
                "doctype": "Custom Field",
                "dt": doctype,
                **field
            }).insert()
            print(f"Created {field['fieldname']} in {doctype}")
        else:
            print(f"{field['fieldname']} already exists in {doctype}")

# Create child table for Additional IDs if it doesn't exist
if not frappe.db.exists("DocType", "Customer Additional ID"):
    child_dt = frappe.get_doc({
        "doctype": "DocType",
        "name": "Customer Additional ID",
        "module": "Selling",
        "istable": 1,
        "fields": [
            {
                "fieldname": "type_name",
                "fieldtype": "Data",
                "label": "Type Name",
                "in_list_view": 1
            },
            {
                "fieldname": "type_code",
                "fieldtype": "Data",
                "label": "Type Code",
                "in_list_view": 1
            },
            {
                "fieldname": "value",
                "fieldtype": "Data",
                "label": "Value",
                "in_list_view": 1
            }
        ]
    })
    child_dt.insert()
    print("Created Customer Additional ID child table")

frappe.db.commit()
print("\nAll custom fields created successfully!")
```

#### Option B: Via UI (Manual - For Individual Fields)

**For Customer:**

1. Go to: **Customize Form** → Select **Customer**
2. Add fields:
   - **VAT Registration Number:**
     - Label: VAT Registration Number
     - Fieldname: `custom_vat_registration_number`
     - Field Type: Data

   - **Additional IDs Table:**
     - Label: Additional IDs
     - Fieldname: `custom_additional_ids`
     - Field Type: Table
     - Options: Customer Additional ID (create child table first)

**For Address:**

1. Go to: **Customize Form** → Select **Address**
2. Add fields:
   - Label: Building Number
   - Fieldname: `custom_building_number`
   - Field Type: Data

   - Label: Area
   - Fieldname: `custom_area`
   - Field Type: Data

**For Sales Invoice:**

1. Go to: **Customize Form** → Select **Sales Invoice**
2. Add field:
   - Label: QR Code
   - Fieldname: `qr_code`
   - Field Type: Long Text

### 3. Create API User

1. Go to: **User List** → **Add User**
2. Fill in details:
   - **Email:** api@yourcompany.com (or any email)
   - **First Name:** API User
   - **Roles:**
     - Sales User
     - Sales Invoice Manager
     - Accounts User
     - Item Manager (optional)
3. Save the user

### 4. Generate API Keys

1. Open the user you just created
2. Scroll to **API Access** section
3. Click **Generate Keys**
4. Copy both **API Key** and **API Secret**
5. Store them securely (you won't be able to see the secret again)

### 5. Set Up Company Permissions

For multi-company setups:

1. Go to: **User Permissions**
2. Add permission:
   - **User:** api@yourcompany.com
   - **Allow:** Company
   - **For Value:** Company A
3. Repeat for other companies as needed

---

## Configuration

### Update Configuration File

1. Navigate to the API directory:

```bash
cd apps/frappe_dotnet/frappe_dotnet/api/
```

2. Copy and edit the configuration:

```bash
cp example_config.json config.json
```

3. Edit `config.json` with your details:

```json
{
  "site_url": "https://your-site.com",
  "api_key": "your_actual_api_key",
  "api_secret": "your_actual_api_secret",
  "companies": [
    {
      "name": "Your Company Name",
      "default_currency": "SAR",
      "default_warehouse": "Stores - YC"
    }
  ],
  "default_customer_group": "Commercial",
  "default_territory": "All Territories"
}
```

**Important:** Add `config.json` to your `.gitignore` to avoid committing credentials!

---

## Testing the API

### Method 1: Using the Python Test Client

1. Navigate to the API directory:

```bash
cd apps/frappe_dotnet/frappe_dotnet/api/
```

2. Update `test_client.py` with your actual item codes and company names

3. Run the test:

```bash
# Basic invoice creation test
python3 test_client.py
```

Edit the `__main__` block to uncomment specific tests:

```python
if __name__ == "__main__":
    # Uncomment the test you want to run:
    test_basic_invoice()       # Test creating invoice
    # test_update_qr_code()    # Test updating QR code
    # test_error_handling()    # Test error scenarios
```

### Method 2: Using cURL

```bash
curl -X POST https://your-site.com/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Your Company",
    "customer_name": "Test Customer",
    "items": [
      {
        "item_code": "ITEM-001",
        "qty": 1,
        "rate": 100
      }
    ]
  }'
```

### Method 3: Using Postman

1. **Create New Request:**
   - Method: POST
   - URL: `https://your-site.com/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice`

2. **Headers:**
   - Key: `Authorization`
   - Value: `token YOUR_KEY:YOUR_SECRET`
   - Key: `Content-Type`
   - Value: `application/json`

3. **Body (raw JSON):**

```json
{
  "company": "Your Company",
  "customer_name": "Test Customer",
  "customer_email": "test@example.com",
  "items": [
    {
      "item_code": "ITEM-001",
      "qty": 10,
      "rate": 100
    }
  ],
  "qr_code": "YOUR_QR_CODE_DATA"
}
```

4. Click **Send**

---

## Verifying Installation

### Check if API is accessible:

```bash
curl -X GET https://your-site.com/api/method/frappe.auth.get_logged_user \
  -H "Authorization: token YOUR_KEY:YOUR_SECRET"
```

Expected response:
```json
{
  "message": "api@yourcompany.com"
}
```

---

## Common Setup Issues

### Issue 1: "Authentication required"

**Cause:** Invalid or missing API credentials

**Solution:**
- Verify API key and secret are correct
- Check if the API user is enabled
- Ensure Authorization header format: `token KEY:SECRET`

### Issue 2: "Permission Denied"

**Cause:** API user lacks required permissions

**Solution:**
- Assign these roles to the API user:
  - Sales User
  - Sales Invoice Manager
  - Accounts User
- Check User Permissions if using multi-company setup

### Issue 3: "Company does not exist"

**Cause:** Company name mismatch

**Solution:**
- Verify exact company name (case-sensitive)
- Check in: **Setup → Company → [Your Company]**

### Issue 4: "Item does not exist"

**Cause:** Invalid item code

**Solution:**
- Verify item codes exist: **Stock → Item**
- Ensure items are not disabled

### Issue 5: QR Code field not updating

**Cause:** Custom field doesn't exist

**Solution:**
- Create custom field (see Step 2)
- Verify field name is exactly `qr_code`

---

## Security Best Practices

1. **Protect API Credentials:**
   - Never commit `config.json` to version control
   - Add to `.gitignore`: `**/config.json`
   - Use environment variables in production

2. **Enable IP Whitelisting:**
   - Go to: **System Settings**
   - Enable "Allow Only IP" and add trusted IPs

3. **Use HTTPS:**
   - Always use SSL certificates in production
   - Never send credentials over HTTP

4. **Limit API User Permissions:**
   - Only grant minimum required permissions
   - Use separate API users for different integrations

5. **Monitor API Usage:**
   - Check logs regularly: **Error Log**
   - Set up alerts for unusual activity

6. **Rotate Keys Regularly:**
   - Generate new API keys every 90 days
   - Revoke old keys immediately

---

## Integration with .NET Applications

### Example C# Integration

```csharp
// Install package: Install-Package RestSharp
using RestSharp;

var client = new RestClient("https://your-site.com");
var request = new RestRequest("/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice", Method.Post);

request.AddHeader("Authorization", "token YOUR_KEY:YOUR_SECRET");
request.AddJsonBody(new
{
    company = "Your Company",
    customer_name = "Customer Name",
    items = new[]
    {
        new { item_code = "ITEM-001", qty = 10, rate = 100.0 }
    }
});

var response = client.Execute(request);
Console.WriteLine(response.Content);
```

---

## Next Steps

1. **Read the API Documentation:**
   - See: `frappe_dotnet/api/README.md`
   - Contains detailed endpoint documentation

2. **Set Up Multi-Company (if needed):**
   - Create user permissions for each company
   - Test with different companies

3. **Implement Error Handling:**
   - Handle all error scenarios in your application
   - Log API responses for debugging

4. **Production Deployment:**
   - Use environment variables for credentials
   - Enable rate limiting
   - Set up monitoring and alerts

5. **ZATCA Compliance (Saudi Arabia):**
   - Generate proper QR codes
   - Test with ZATCA validation tools
   - Ensure invoice data meets requirements

---

## Support Resources

- **API Documentation:** `frappe_dotnet/api/README.md`
- **ERPNext Documentation:** https://docs.erpnext.com
- **Frappe Framework:** https://frappeframework.com
- **Error Logs:** ERPNext → Error Log

---

## Checklist

Before going to production:

- [ ] Custom QR Code field created
- [ ] API user created with proper roles
- [ ] API keys generated and stored securely
- [ ] Company permissions configured
- [ ] Test invoice created successfully
- [ ] Error handling tested
- [ ] HTTPS enabled
- [ ] IP whitelisting configured (optional)
- [ ] Monitoring set up
- [ ] Documentation reviewed

---

## Quick Reference

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice` | POST | Create invoice |
| `/api/method/frappe_dotnet.api.sales_invoice.update_invoice_qr_code` | POST | Update QR code |

### Required Roles

- Sales User
- Sales Invoice Manager
- Accounts User

### Configuration Files

- `frappe_dotnet/api/config.json` - Your configuration (create from example)
- `frappe_dotnet/api/example_config.json` - Template
- `frappe_dotnet/api/test_client.py` - Test script

---

## Getting Help

If you encounter issues:

1. Check error logs in ERPNext
2. Review the API documentation
3. Verify your configuration
4. Test with the provided test client
5. Check Frappe forum: https://discuss.frappe.io

---

**Last Updated:** 2025-12-11
**Version:** 1.0.0
