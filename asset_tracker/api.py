# Copyright (c) 2026, Pragati Hegde and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_days, cint, flt, getdate, today


@frappe.whitelist()
def get_employee_assets(employee: str) -> list[dict]:
	"""
	Callable API function:
	Returns all assets currently assigned to a given employee,
	including their condition and current value.
	"""
	if not employee:
		frappe.throw("Employee parameter is required.")

	# Validate employee exists
	if not frappe.db.exists("Employee", employee):
		frappe.throw(f"Employee {employee} not found.")

	# Fetch assigned assets
	assets = frappe.get_all(
		"Asset",
		filters={"current_employee": employee, "status": "Assigned"},
		fields=[
			"name",
			"asset_name",
			"category",
			"department",
			"status",
			"condition",
			"purchase_date",
			"purchase_cost",
			"current_value",
			"last_maintenance_date",
			"next_maintenance_date",
		],
		order_by="creation desc",
	)

	# Format values
	for asset in assets:
		asset["current_value"] = flt(asset.get("current_value"), 2)
		asset["purchase_cost"] = flt(asset.get("purchase_cost"), 2)

	return assets


@frappe.whitelist()
def get_upcoming_maintenance(days: int = 7) -> list[dict]:
	"""
	Callable API function:
	Returns assets with maintenance due within a specified number of days,
	for use in dashboard views.
	"""
	days_count = cint(days) or 7
	current_today = getdate(today())
	target_date = getdate(add_days(today(), days_count))

	maintenances = frappe.get_all(
		"Asset Maintenance",
		filters={
			"status": ["in", ["Scheduled", "In Progress"]],
			"scheduled_date": ["between", [current_today, target_date]],
		},
		fields=[
			"name",
			"asset",
			"maintenance_type",
			"scheduled_date",
			"status",
			"service_provider",
			"maintenance_notes",
		],
		order_by="scheduled_date asc",
	)

	# Enrich with Asset details
	for m in maintenances:
		asset_info = frappe.db.get_value(
			"Asset",
			m["asset"],
			["asset_name", "category", "current_employee", "condition", "status as asset_status"],
			as_dict=True,
		)
		if asset_info:
			m["asset_name"] = asset_info.asset_name
			m["category"] = asset_info.category
			m["current_employee"] = asset_info.current_employee
			m["condition"] = asset_info.condition
			m["asset_status"] = asset_info.asset_status

	return maintenances
