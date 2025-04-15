# Copyright (c) 2025, BOT SOlutions and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe import _
from frappe.model.document import Document



class SaudiCompanyNationalAddress(Document):
    def validate(self):
        if not self.cr_number:
            frappe.throw(_("CR Number is required"))

    @frappe.whitelist()
    def fetch_national_address(self):
        if not self.cr_number:
            frappe.throw(_("Please enter a CR Number first"))
        
        api_url = f"https://api.wathq.sa/spl/national/address/info/{self.cr_number}"
        headers = {
            'accept': 'application/json',
            'apiKey': 'VES29G3JAfWOGu0eo0AxNaNbpoJHLZGq'
        }
        
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                address_data = data[0]
                
                # Map API response to document fields
                self.company_title = address_data.get('title')
                self.company_status = address_data.get('status')
                self.address_1 = address_data.get('address')
                self.address_2 = address_data.get('address2')
                self.latitude = address_data.get('latitude')
                self.longitude = address_data.get('longitude')
                self.building_number = address_data.get('buildingNumber')
                self.street = address_data.get('street')
                self.district = address_data.get('district')
                self.district_id = address_data.get('districtId')
                self.city = address_data.get('city')
                self.city_id = address_data.get('cityId')
                self.post_code = address_data.get('postCode')
                self.additional_number = address_data.get('additionalNumber')
                self.region_name = address_data.get('regionName')
                self.region_id = address_data.get('regionId')
                self.is_primary_address = 1 if address_data.get('isPrimaryAddress') == "true" else 0
                self.unit_number = address_data.get('unitNumber')
                self.restriction = address_data.get('restriction')
                self.pk_address_id = address_data.get('pkAddressId')
                
                frappe.msgprint(_("Address details fetched successfully"))
                return True
            else:
                frappe.throw(_("No address data found for this CR Number"))
                
        except requests.exceptions.RequestException as e:
            frappe.throw(_("Error fetching address: {0}").format(str(e)))
        except json.JSONDecodeError:
            frappe.throw(_("Invalid response from API"))


@frappe.whitelist()
def convert_to_customer(docname):
    try:
        synced_company = frappe.get_doc('Saudi Company National Address', docname)
        frappe.msgprint(f"Processing Company: {synced_company.company_title}")

        customer = frappe.db.get_value('Customer', {'customer_name': synced_company.company_title}, 'name')
        frappe.msgprint(f"Customer lookup for {synced_company.company_title}: {customer or 'Not found'}")

        if not customer:
            frappe.msgprint(f"Creating new customer: {synced_company.company_title}")
            try:
                customer_data = frappe.get_doc({
                    'doctype': 'Customer',
                    'customer_name': synced_company.company_title,
                    'customer_type': 'Company',
                    'customer_group': 'Commercial',
                    'territory': 'Saudi Arabia'
                })

                fieldnames = [df.fieldname for df in customer_data.meta.fields]

                if 'custom_cr_number' in fieldnames:
                    customer_data.custom_cr_number = synced_company.cr_number

                customer = customer_data.insert().name
                frappe.msgprint(f"Customer created: {customer}")
            except Exception as e:
                frappe.log_error(f"Failed to create customer: {str(e)}", "Customer Creation Error")
                frappe.throw(_("Error creating customer: ") + str(e))

            try:
                if 'custom_additional_ids' in fieldnames:
                    customer_data.append("custom_additional_ids", {
                        "type_name": "Commercial Registration Number",
                        "type_code": "CRN",
                        "value": synced_company.cr_number
                    })
                    customer_data.save()
            except Exception as e:
                frappe.log_error(f"Failed to add CRN to child table: {str(e)}", "Child Table Error")

            try:
                customer_address = frappe.get_doc({
                    'doctype': 'Address',
                    'address_title': synced_company.company_title,
                    'address_line1': f"{synced_company.address_1} {synced_company.street or ''} {synced_company.building_number or ''}".strip(),
                    'address_line2': synced_company.address_2,
                    'custom_building_number': synced_company.building_number,
                    'city': synced_company.city,
                    'custom_area': synced_company.district,
                    'country': 'Saudi Arabia',
                    'state': synced_company.region_name,
                    'pincode': synced_company.post_code,
                    "links": [
                        {
                            "link_doctype": "Customer",
                            "link_name": customer
                        }
                    ]
                })
                customer_address.insert()
                frappe.msgprint(f"Customer address created for: {customer}")
            except Exception as e:
                frappe.log_error(f"Failed to create address: {str(e)}", "Address Creation Error")
                frappe.throw(_("Error creating customer address: ") + str(e))

        return f"Customer {synced_company.company_title} created successfully."

    except Exception as e:
        frappe.log_error(f"Conversion to Customer failed: {str(e)}", "Customer Conversion Error")
        frappe.throw(_("Conversion to Customer failed: ") + str(e))

def revert_status(doc, method):
    # Handle single or bulk deletions
    customers = doc if isinstance(doc, list) else [doc]

    for customer in customers:  # Loop through the customers
        customer_name = customer.get("customer_name")
        if customer_name:
            # Fetch the corresponding record in your custom doctype
            synced_company = frappe.get_doc("Saudi Company National Address", {'company_title': customer_name})
            # Update the status to 'Draft'
            synced_company.status = "Draft"
            synced_company.save()

    # Refresh the list view to reflect changes
    frappe.publish_realtime('list_refresh', {"doctype": "Saudi Company National Address"})