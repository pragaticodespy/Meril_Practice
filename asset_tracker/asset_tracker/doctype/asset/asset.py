# Copyright (c) 2026, Pragati Hegde and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate, today


class Asset(Document):
	def validate(self):
		self.validate_values()
		self.validate_disposal()

	def validate_values(self):
		if self.purchase_cost is not None and flt(self.purchase_cost) < 0:
			frappe.throw("Purchase cost cannot be negative.")

		if self.current_value is None and self.purchase_cost is not None:
			self.current_value = flt(self.purchase_cost)

		if self.current_value is not None and flt(self.current_value) < 0:
			frappe.throw("Current value cannot be negative.")

	def validate_disposal(self):
		if self.status == "Disposed":
			if not self.disposal_date:
				self.disposal_date = today()
			if not self.disposal_reason:
				frappe.throw("Disposal reason is mandatory when disposing an asset.")
			if self.current_employee:
				frappe.throw("Cannot dispose an asset while it is assigned to an employee. Please return the asset first.")

		# If already disposed in database, cannot be reactivated or modified back
		if not self.is_new():
			previous_status = frappe.db.get_value("Asset", self.name, "status")
			if previous_status == "Disposed" and self.status != "Disposed":
				frappe.throw("A disposed asset cannot be reactivated.")


def process_monthly_depreciation():
	"""
	Scheduled task:
	Monthly depreciation runs automatically and must not run twice for the same asset in the same month.
	If an asset's value has already reached zero or it is disposed, skip it.
	"""
	current_today = getdate(today())
	assets = frappe.get_all(
		"Asset",
		filters={"status": ["!=", "Disposed"], "current_value": [">", 0]},
		fields=["name", "category", "purchase_cost", "current_value", "last_depreciation_date"],
	)

	for asset_data in assets:
		# Check if already depreciated in current month
		last_dep = asset_data.get("last_depreciation_date")
		if last_dep:
			last_dep_date = getdate(last_dep)
			if (
				last_dep_date.year == current_today.year
				and last_dep_date.month == current_today.month
			):
				continue

		depreciate_single_asset(asset_data["name"], current_today)


def depreciate_single_asset(asset_name: str, posting_date=None):
	"""Calculate and apply depreciation for one asset."""
	if not posting_date:
		posting_date = getdate(today())

	asset_doc = frappe.get_doc("Asset", asset_name)
	if asset_doc.status == "Disposed" or flt(asset_doc.current_value) <= 0:
		return

	if asset_doc.last_depreciation_date:
		last_dep_date = getdate(asset_doc.last_depreciation_date)
		if (
			last_dep_date.year == posting_date.year
			and last_dep_date.month == posting_date.month
		):
			return

	if not asset_doc.category:
		return

	depreciation_rate = flt(
		frappe.db.get_value("Asset Category", asset_doc.category, "depreciation_rate")
	)
	if depreciation_rate <= 0:
		return

	# Monthly straight-line depreciation = purchase_cost * (annual_rate / 100) / 12
	monthly_dep_amount = round(
		flt(asset_doc.purchase_cost) * (depreciation_rate / 100.0) / 12.0, 2
	)

	if monthly_dep_amount <= 0:
		return

	value_before = flt(asset_doc.current_value)
	dep_amount = min(monthly_dep_amount, value_before)
	value_after = round(max(0.0, value_before - dep_amount), 2)

	# Update Asset record
	asset_doc.current_value = value_after
	asset_doc.last_depreciation_date = posting_date
	asset_doc.flags.ignore_validate_update_after_submit = True
	asset_doc.save(ignore_permissions=True)

	# Record in Asset Depreciation Log
	dep_log = frappe.get_doc(
		{
			"doctype": "Asset Depreciation Log",
			"asset": asset_doc.name,
			"category": asset_doc.category,
			"depreciation_date": posting_date,
			"annual_rate": depreciation_rate,
			"value_before": value_before,
			"depreciation_amount": dep_amount,
			"value_after": value_after,
			"notes": f"Automatic monthly depreciation for {posting_date.strftime('%B %Y')}",
		}
	)
	dep_log.insert(ignore_permissions=True)


def get_permission_query_conditions(user: str) -> str:
	"""
	Row-level security:
	Employees see only assets assigned to them.
	Asset Managers, Finance, and System Managers see all assets.
	"""
	if not user:
		user = frappe.session.user

	roles = frappe.get_roles(user)
	if any(r in ["System Manager", "Administrator", "Asset Manager", "Finance"] for r in roles):
		return ""

	if "Employee" in roles:
		employee_names = frappe.get_all(
			"Employee",
			filters={"user_id": user},
			pluck="name",
		)
		if not employee_names:
			# Try matching by user email
			employee_names = frappe.get_all(
				"Employee",
				filters={"email": user},
				pluck="name",
			)

		if employee_names:
			formatted_names = ", ".join([frappe.db.escape(e) for e in employee_names])
			return f"`tabAsset`.`current_employee` in ({formatted_names})"

		return "1=2"

	return ""


def has_permission(doc, user: str = None, permission_type: str = None) -> bool:
	if not user:
		user = frappe.session.user

	roles = frappe.get_roles(user)
	if any(r in ["System Manager", "Administrator", "Asset Manager", "Finance"] for r in roles):
		return True

	if "Employee" in roles:
		employee_names = frappe.get_all(
			"Employee",
			filters={"user_id": user},
			pluck="name",
		)
		if not employee_names:
			employee_names = frappe.get_all(
				"Employee",
				filters={"email": user},
				pluck="name",
			)
		return doc.current_employee in employee_names

	return False

