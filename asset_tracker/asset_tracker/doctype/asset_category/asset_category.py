# Copyright (c) 2026, Pragati Hegde and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class AssetCategory(Document):
	def validate(self):
		if self.depreciation_rate is not None and (self.depreciation_rate < 0 or self.depreciation_rate > 100):
			frappe.throw("Depreciation rate must be between 0% and 100%.")
