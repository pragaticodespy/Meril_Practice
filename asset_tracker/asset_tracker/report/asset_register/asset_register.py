# Copyright (c) 2026, Pragati Hegde and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data, total_cost, total_value = get_data(filters)
	report_summary = get_report_summary(data, total_cost, total_value)
	chart = get_chart_data(data)

	# Append explicit summary row at bottom
	if data:
		summary_row = {
			"asset": "<b>Total</b>",
			"asset_name": "",
			"category": "",
			"department": "",
			"status": "",
			"condition": "",
			"current_employee": "",
			"last_maintenance_date": "",
			"purchase_cost": total_cost,
			"current_value": total_value,
		}
		data.append(summary_row)

	return columns, data, None, chart, report_summary


def get_columns():
	can_see_values = True
	roles = frappe.get_roles(frappe.session.user)
	if "Employee" in roles and not any(
		r in ["System Manager", "Administrator", "Asset Manager", "Finance"] for r in roles
	):
		can_see_values = False

	columns = [
		{
			"label": _("Asset ID"),
			"fieldname": "asset",
			"fieldtype": "Link",
			"options": "Asset",
			"width": 140,
		},
		{
			"label": _("Asset Name"),
			"fieldname": "asset_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("Category"),
			"fieldname": "category",
			"fieldtype": "Link",
			"options": "Asset Category",
			"width": 140,
		},
		{
			"label": _("Department"),
			"fieldname": "department",
			"fieldtype": "Data",
			"width": 130,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"label": _("Condition"),
			"fieldname": "condition",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Assigned Employee"),
			"fieldname": "current_employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 160,
		},
		{
			"label": _("Last Maintenance Date"),
			"fieldname": "last_maintenance_date",
			"fieldtype": "Date",
			"width": 150,
		},
	]

	if can_see_values:
		columns.extend(
			[
				{
					"label": _("Purchase Cost"),
					"fieldname": "purchase_cost",
					"fieldtype": "Currency",
					"width": 130,
				},
				{
					"label": _("Current Value"),
					"fieldname": "current_value",
					"fieldtype": "Currency",
					"width": 130,
				},
			]
		)

	return columns


def get_data(filters):
	conditions = {}

	if filters.get("category"):
		conditions["category"] = filters.get("category")
	if filters.get("status"):
		conditions["status"] = filters.get("status")
	if filters.get("department"):
		conditions["department"] = filters.get("department")

	# Fetch assets
	assets = frappe.get_all(
		"Asset",
		filters=conditions,
		fields=[
			"name as asset",
			"asset_name",
			"category",
			"department",
			"status",
			"condition",
			"current_employee",
			"last_maintenance_date",
			"purchase_cost",
			"current_value",
		],
		order_by="creation desc",
	)

	total_cost = 0.0
	total_value = 0.0

	for item in assets:
		item["purchase_cost"] = flt(item.get("purchase_cost"), 2)
		item["current_value"] = flt(item.get("current_value"), 2)
		total_cost += item["purchase_cost"]
		total_value += item["current_value"]

	return assets, round(total_cost, 2), round(total_value, 2)


def get_report_summary(data, total_cost, total_value):
	total_assets = len(data)
	return [
		{
			"value": total_assets,
			"label": _("Total Assets"),
			"datatype": "Int",
		},
		{
			"value": total_cost,
			"label": _("Total Purchase Cost"),
			"datatype": "Currency",
			"currency": frappe.defaults.get_global_default("currency") or "INR",
		},
		{
			"value": total_value,
			"label": _("Total Current Value"),
			"datatype": "Currency",
			"currency": frappe.defaults.get_global_default("currency") or "INR",
		},
	]


def get_chart_data(data):
	if not data:
		return None

	category_counts = {}
	for row in data:
		cat = row.get("category") or "Uncategorized"
		category_counts[cat] = category_counts.get(cat, 0) + 1

	labels = list(category_counts.keys())
	values = list(category_counts.values())

	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": _("Assets"), "values": values}],
		},
		"type": "bar",
		"colors": ["#5e64ff", "#28a745", "#ffc107", "#dc3545"],
	}
