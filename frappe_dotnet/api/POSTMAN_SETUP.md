# Postman Setup Guide for Sales Invoice API

## Quick Start

This guide will help you set up and test the Sales Invoice API using Postman.

---

## Step 1: Import the Collection

1. **Open Postman**

2. **Import Collection:**
   - Click **Import** button (top left)
   - Select **Upload Files**
   - Navigate to: `frappe_dotnet/api/Postman_Collection.json`
   - Click **Open**
   - Click **Import**

3. **Collection Imported:**
   - You should now see "Frappe DotNet - Sales Invoice API" in your Collections

---

## Step 2: Configure Variables

The collection uses variables to make it easy to switch between environments and update credentials.

### Set Collection Variables:

1. **Open the Collection:**
   - Click on "Frappe DotNet - Sales Invoice API"

2. **Go to Variables Tab:**
   - Click on the **Variables** tab

3. **Update the Following Variables:**

   | Variable | Current Value | Description |
   |----------|---------------|-------------|
   | `base_url` | `https://techbrightsolutions.saas-erp.in` | Your ERPNext URL (already set) |
   | `api_key` | `YOUR_API_KEY_HERE` | Your API Key from ERPNext |
   | `api_secret` | `YOUR_API_SECRET_HERE` | Your API Secret from ERPNext |

4. **Save the Collection** (Ctrl+S or Cmd+S)

---

## Step 3: Generate API Keys in ERPNext

If you haven't already created API keys:

1. **Login to ERPNext:**
   - Go to: https://techbrightsolutions.saas-erp.in

2. **Navigate to User:**
   - Go to **User List**
   - Select your user (or create an API user)

3. **Generate Keys:**
   - Scroll to **API Access** section
   - Click **Generate Keys**
   - **Copy both the API Key and API Secret**
   - Store them securely (you won't see the secret again)

4. **Update Postman Variables:**
   - Paste the API Key into `api_key` variable
   - Paste the API Secret into `api_secret` variable
   - Save the collection

---

## Step 4: Test Authentication

Before creating invoices, verify your credentials work:

1. **Open Request:**
   - Expand the collection
   - Click on **"7. Test Authentication"**

2. **Send Request:**
   - Click **Send** button

3. **Expected Response:**
   ```json
   {
       "message": "your-email@example.com"
   }
   ```

4. **If you get an error:**
   - Verify API key and secret are correct
   - Check if the user is enabled in ERPNext
   - Ensure the user has proper permissions

---

## Step 5: Update Request Data

Before testing invoice creation, update the request bodies with your actual data:

### Update These Fields:

1. **Company Name:**
   - Replace `"ZATCA Company"` with your actual company name
   - Go to ERPNext → **Setup → Company** to see available companies

2. **Item Codes:**
   - Replace `"ITEM-001"`, `"ITEM-002"` with your actual item codes
   - Go to ERPNext → **Stock → Item** to see available items

3. **Customer Names:**
   - Replace with actual customer names or test names
   - The API will create new customers automatically

---

## Step 6: Test Invoice Creation

### Test 1: Basic Invoice (Recommended First Test)

1. **Open Request:**
   - Click on **"2. Create Sales Invoice - Basic (Minimal Fields)"**

2. **Update JSON Body:**
   ```json
   {
       "company": "Your Actual Company Name",
       "customer_name": "Test Customer 001",
       "items": [
           {
               "item_code": "YOUR-ITEM-CODE",
               "qty": 1,
               "rate": 100
           }
       ]
   }
   ```

3. **Send Request:**
   - Click **Send**

4. **Expected Response:**
   ```json
   {
       "message": {
           "success": true,
           "message": "Sales Invoice SINV-2025-00001 created successfully",
           "invoice_name": "SINV-2025-00001",
           "invoice_url": "https://techbrightsolutions.saas-erp.in/app/sales-invoice/SINV-2025-00001",
           "customer": "Test Customer 001",
           "grand_total": 100.0
       }
   }
   ```

5. **Verify in ERPNext:**
   - Click on the `invoice_url` in the response
   - Or go to: **Selling → Sales Invoice**

---

### Test 2: Complete Invoice with Address

1. **Open Request:**
   - Click on **"1. Create Sales Invoice - Complete (with Address & VAT)"**

2. **Update JSON Body** with your data:
   - Company name
   - Customer details
   - Item codes
   - Address information
   - VAT and CRN numbers

3. **Send Request**

4. **Verify:**
   - Check the Sales Invoice
   - Check the Customer record (should have VAT number)
   - Check the Address linked to the customer

---

## Available Requests in the Collection

| # | Request Name | Description |
|---|--------------|-------------|
| 1 | Create Sales Invoice - Complete | Full example with customer, address, VAT, and CRN |
| 2 | Create Sales Invoice - Basic | Minimal required fields only |
| 3 | Create Sales Invoice - With Submit | Auto-submit invoice after creation |
| 4 | Create Sales Invoice - Multi-Item | Multiple items with different discounts |
| 5 | Create Sales Invoice - Custom Fields | Example with additional custom fields |
| 6 | Update Invoice QR Code | Update QR code for existing invoice |
| 7 | Test Authentication | Verify API credentials |

---

## Request Parameters Guide

### Required Parameters

```json
{
    "company": "Your Company Name",           // Must exist in ERPNext
    "customer_name": "Customer Name",         // Will be created if doesn't exist
    "items": [                                // At least one item required
        {
            "item_code": "ITEM-001",          // Must exist in ERPNext
            "qty": 10,                        // Required
            "rate": 100                       // Optional (uses item default)
        }
    ]
}
```

### Customer Details (Optional)

```json
{
    "customer_email": "customer@example.com",
    "customer_phone": "+966501234567",
    "customer_type": "Company",               // or "Individual"
    "customer_group": "Commercial",
    "territory": "All Territories",
    "custom_vat_registration_number": "312038504300003",
    "commercial_registration_number": "1010394694"
}
```

### Address Details (Optional)

```json
{
    "address_line1": "King Fahd Road",
    "address_line2": "Building 123, Floor 4",
    "custom_building_number": "7890",         // ZATCA required
    "custom_area": "Al Olaya District",       // ZATCA required
    "city": "Riyadh",
    "state": "Riyadh Region",
    "pincode": "12345",
    "country": "Saudi Arabia"
}
```

### Invoice Details (Optional)

```json
{
    "posting_date": "2025-12-11",            // Format: YYYY-MM-DD
    "due_date": "2025-12-31",                // Format: YYYY-MM-DD
    "currency": "SAR",                       // Defaults to company currency
    "qr_code": "BASE64_ENCODED_QR_DATA",
    "submit_invoice": true                   // Auto-submit after creation
}
```

---

## Common Issues and Solutions

### Issue 1: "Authentication required"

**Error:**
```json
{
    "exc_type": "AuthenticationError",
    "message": "Authentication required"
}
```

**Solutions:**
- Verify `api_key` and `api_secret` variables are set correctly
- Check Authorization header: `token {{api_key}}:{{api_secret}}`
- Ensure the API user is enabled in ERPNext

---

### Issue 2: "Company does not exist"

**Error:**
```json
{
    "message": {
        "success": false,
        "message": "Company 'XYZ' does not exist. Please check the company name."
    }
}
```

**Solutions:**
- Go to ERPNext → **Setup → Company**
- Copy the exact company name (case-sensitive)
- Update the `company` field in your request

---

### Issue 3: "Item does not exist"

**Error:**
```json
{
    "message": {
        "success": false,
        "message": "Item 'ITEM-001' does not exist in the system"
    }
}
```

**Solutions:**
- Go to ERPNext → **Stock → Item**
- Verify the item code exists
- Copy the exact item code
- Ensure the item is not disabled

---

### Issue 4: "Permission Denied"

**Error:**
```json
{
    "message": {
        "success": false,
        "message": "Permission Denied: You don't have permission to create invoices"
    }
}
```

**Solutions:**
- Go to ERPNext → **User → [Your API User]**
- Ensure these roles are assigned:
  - Sales User
  - Sales Invoice Manager
  - Accounts User
- Check User Permissions for multi-company setups

---

### Issue 5: QR Code field not updating

**Solutions:**
- Create the custom field `qr_code` in Sales Invoice
- See: [SETUP_GUIDE.md](../../SETUP_GUIDE.md) Step 2
- Or go to: **Customize Form → Sales Invoice**
- Add field: `qr_code` (Long Text)

---

## Testing Workflow

### Recommended Testing Order:

1. **Test Authentication** (Request #7)
   - Verify credentials work

2. **Create Basic Invoice** (Request #2)
   - Test with minimal fields
   - Use existing customer name if available

3. **Verify in ERPNext**
   - Check if invoice was created
   - Verify data is correct

4. **Create Complete Invoice** (Request #1)
   - Test with new customer
   - Include all address fields
   - Add VAT and CRN numbers

5. **Verify Customer Creation**
   - Go to: **Selling → Customer**
   - Check if customer was created
   - Verify VAT number is set
   - Check additional IDs table for CRN

6. **Verify Address Creation**
   - Open the customer
   - Go to **Address & Contact** section
   - Verify billing address was created
   - Check custom fields (building number, area)

7. **Update QR Code** (Request #6)
   - Use an invoice name from previous tests
   - Test QR code update

---

## Tips for Effective Testing

1. **Use Postman Environment Variables:**
   - Create different environments for dev/staging/production
   - Switch between environments easily

2. **Save Responses:**
   - Save successful responses as examples
   - Helps document expected behavior

3. **Use Postman Tests:**
   - Add test scripts to validate responses
   - Example:
     ```javascript
     pm.test("Invoice created successfully", function() {
         var jsonData = pm.response.json();
         pm.expect(jsonData.message.success).to.be.true;
     });
     ```

4. **Create Folders:**
   - Organize requests by functionality
   - Group related tests together

5. **Use Pre-request Scripts:**
   - Generate dynamic data (dates, random numbers)
   - Example:
     ```javascript
     pm.collectionVariables.set("today", new Date().toISOString().split('T')[0]);
     ```

---

## Export and Share

### Export Collection:

1. Click on collection (**...**)
2. Select **Export**
3. Choose **Collection v2.1**
4. Save JSON file
5. Share with team members

### Export Environment:

1. Click on Environments
2. Select your environment
3. Click **...** → **Export**
4. Save JSON file

---

## Next Steps

1. **Complete Setup:**
   - See: [SETUP_GUIDE.md](../../SETUP_GUIDE.md)
   - Create required custom fields

2. **Read Documentation:**
   - See: [README.md](README.md)
   - Complete API documentation with all parameters

3. **Integration:**
   - Use Postman examples to build your application
   - Copy cURL commands for terminal testing
   - Generate code snippets (Code button in Postman)

---

## Getting Help

If you encounter issues:

1. Check ERPNext **Error Log**
   - Go to: **Setup → Error Log**
   - Filter by date and search for your request

2. Check Response Status:
   - 200 = Success
   - 401 = Authentication Error
   - 403 = Permission Error
   - 417 = Validation Error
   - 500 = Server Error

3. Review Documentation:
   - [API Documentation](README.md)
   - [Setup Guide](../../SETUP_GUIDE.md)

---

## Support

For additional help:
- Check ERPNext documentation: https://docs.erpnext.com
- Review Frappe API docs: https://frappeframework.com/docs/user/en/api

---

**Base URL:** https://techbrightsolutions.saas-erp.in

**API Endpoints:**
- Create Invoice: `/api/method/frappe_dotnet.api.sales_invoice.create_sales_invoice`
- Update QR Code: `/api/method/frappe_dotnet.api.sales_invoice.update_invoice_qr_code`

**Last Updated:** 2025-12-11
