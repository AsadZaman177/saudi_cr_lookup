# Copyright (c) 2025, BOT SOlutions and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.utils import nowdate
from frappe.model.document import Document


class SaudiCompany(Document):
    def validate(self):
        if not self.cr_national_number:
            frappe.throw("CR National Number is required")

    @frappe.whitelist()
    def fetch_data(self):
        """Fetch data from Wathq API and update the document"""
        if not self.cr_national_number:
            frappe.throw("CR National Number is required")

        settings = frappe.get_doc("Saudi CR Lookup Settings")
        api_key = settings.get_password("consumer_id")
        sandbox = settings.is_sandbox

        base_url = "https://api.wathq.sa/sandbox" if sandbox else "https://api.wathq.sa"
        url = f"{base_url}/commercial-registration/fullinfo/{self.cr_national_number}?language=en"

        headers = {
            "accept": "application/json",
            "apiKey": api_key
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            cr_number = data.get("crNumber")
            existing = frappe.get_all("Saudi Company", filters={"cr_number": cr_number, "name": ["!=", self.name]})
            if existing:
                frappe.msgprint("A company with this CR number already exists.")
                return

            is_update = bool(self.cr_number)

            self.cr_number = cr_number
            self.company_name = data.get("name")
            self.status = data.get("status", {}).get("name")
            self.last_updated = nowdate()
            self.raw_response = json.dumps(data, indent=2, ensure_ascii=False)

            if is_update:
                frappe.msgprint("Company data updated successfully.")
            else:
                frappe.msgprint("Company data fetched successfully.")
                
            return data

        except Exception as e:
            frappe.throw(f"Failed to fetch data: {str(e)}")
