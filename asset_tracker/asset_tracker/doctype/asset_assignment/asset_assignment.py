# Copyright (c) 2026, Pragati Hegde and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class AssetAssignment(Document):
	def validate(self):
		self.validate_asset_status()
		self.validate_assignment_rules()
		self.validate_return_rules()

	def validate_asset_status(self):
		asset = frappe.get_doc("Asset", self.asset)
		if asset.status == "Disposed":
			frappe.throw(f"Asset {self.asset} is disposed and cannot be assigned.")

	def validate_assignment_rules(self):
		if self.status == "Active":
			# Rule: An asset cannot be assigned to a new employee while it is still assigned to someone else
			existing_active = frappe.db.get_value(
				"Asset Assignment",
				{"asset": self.asset, "status": "Active", "name": ["!=", self.name]},
				["name", "employee"],
				as_dict=True,
			)
			if existing_active:
				frappe.throw(
					f"Asset {self.asset} is currently assigned to employee {existing_active.employee} "
					f"under Assignment {existing_active.name}. It cannot be assigned until it is returned."
				)

			asset_current_emp = frappe.db.get_value("Asset", self.asset, "current_employee")
			if asset_current_emp and asset_current_emp != self.employee:
				frappe.throw(
					f"Asset {self.asset} is currently held by {asset_current_emp}. Please process return before reassignment."
				)

			# Rule: The system must warn when an employee is approaching a three-asset holding limit before allowing a fourth assignment.
			active_count = frappe.db.count(
				"Asset Assignment",
				{"employee": self.employee, "status": "Active", "name": ["!=", self.name]},
			)

			if active_count >= 3:
				frappe.msgprint(
					msg=(
						f"Warning: Employee {self.employee} currently holds {active_count} active assets "
						f"and has reached or approached the 3-asset holding limit before this 4th assignment."
					),
					title="Asset Holding Limit Warning",
					indicator="orange",
					alert=True,
				)

	def validate_return_rules(self):
		if self.status == "Returned":
			# Rule: When returned, the condition at return is mandatory.
			if not self.return_condition:
				frappe.throw("Condition at return is mandatory when returning an asset.")
			if not self.return_date:
				self.return_date = today()

	def on_update(self):
		self.sync_asset_state()

	def sync_asset_state(self):
		"""Synchronize status and custodian on the Asset master record."""
		if self.status == "Active":
			frappe.db.set_value(
				"Asset",
				self.asset,
				{
					"status": "Assigned",
					"current_employee": self.employee,
					"condition": self.issue_condition,
				},
				update_modified=True,
			)
		elif self.status == "Returned":
			frappe.db.set_value(
				"Asset",
				self.asset,
				{
					"status": "Available",
					"current_employee": None,
					"condition": self.return_condition,
				},
				update_modified=True,
			)


def get_permission_query_conditions(user: str) -> str:
	if not user:
		user = frappe.session.user

	roles = frappe.get_roles(user)
	if any(r in ["System Manager", "Administrator", "Asset Manager", "Finance"] for r in roles):
		return ""

	if "Employee" in roles:
		employee_names = frappe.get_all("Employee", filters={"user_id": user}, pluck="name")
		if not employee_names:
			employee_names = frappe.get_all("Employee", filters={"email": user}, pluck="name")

		if employee_names:
			formatted_names = ", ".join([frappe.db.escape(e) for e in employee_names])
			return f"`tabAsset Assignment`.`employee` in ({formatted_names})"

		return "1=2"

	return ""
