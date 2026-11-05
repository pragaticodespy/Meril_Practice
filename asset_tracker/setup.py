
import json
import frappe
from frappe.utils import add_days, today


def after_migrate():
	"""Setup roles, dashboard charts, number cards, and workspace."""
	setup_roles()
	setup_number_cards()
	setup_dashboard_charts()
	setup_workspace()
	frappe.db.commit()


def setup_roles():
	roles = [
		{"role_name": "Asset Manager", "desk_access": 1},
		{"role_name": "Finance", "desk_access": 1},
		{"role_name": "Employee", "desk_access": 1},
	]

	for r in roles:
		if not frappe.db.exists("Role", r["role_name"]):
			doc = frappe.new_doc("Role")
			doc.role_name = r["role_name"]
			doc.desk_access = r["desk_access"]
			doc.insert(ignore_permissions=True)


def setup_number_cards():
	cards = [
		{
			"name": "Total Assets",
			"label": "Total Assets",
			"document_type": "Asset",
			"function": "Count",
			"filters_json": json.dumps([["Asset", "status", "!=", "Disposed"]]),
			"color": "#5e64ff",
		},
		{
			"name": "Total Asset Valuation",
			"label": "Total Valuation",
			"document_type": "Asset",
			"function": "Sum",
			"aggregate_function_based_on": "current_value",
			"filters_json": json.dumps([["Asset", "status", "!=", "Disposed"]]),
			"color": "#28a745",
		},
		{
			"name": "Active Assignments",
			"label": "Assigned Assets",
			"document_type": "Asset Assignment",
			"function": "Count",
			"filters_json": json.dumps([["Asset Assignment", "status", "=", "Active"]]),
			"color": "#17a2b8",
		},
		{
			"name": "Maintenance Due Soon",
			"label": "Maintenance Due (7 Days)",
			"document_type": "Asset Maintenance",
			"function": "Count",
			"filters_json": json.dumps(
				[
					["Asset Maintenance", "status", "=", "Scheduled"],
				]
			),
			"color": "#ffc107",
		},
	]

	for card_data in cards:
		if not frappe.db.exists("Number Card", card_data["name"]):
			card = frappe.new_doc("Number Card")
			card.name = card_data["name"]
			card.label = card_data["label"]
			card.document_type = card_data["document_type"]
			card.function = card_data["function"]
			card.aggregate_function_based_on = card_data.get("aggregate_function_based_on")
			card.filters_json = card_data["filters_json"]
			card.color = card_data.get("color")
			card.is_standard = 0
			card.module = "Asset Tracker"
			card.insert(ignore_permissions=True)


def setup_dashboard_charts():
	charts = [
		{
			"name": "Assets by Status",
			"chart_name": "Assets by Status",
			"document_type": "Asset",
			"chart_type": "Group By",
			"group_by_type": "Count",
			"group_by_based_on": "status",
			"type": "Donut",
			"filters_json": "[]",
		},
		{
			"name": "Assets by Category",
			"chart_name": "Assets by Category",
			"document_type": "Asset",
			"chart_type": "Group By",
			"group_by_type": "Count",
			"group_by_based_on": "category",
			"type": "Bar",
			"filters_json": "[]",
		},
	]

	for chart_data in charts:
		if not frappe.db.exists("Dashboard Chart", chart_data["name"]):
			chart = frappe.new_doc("Dashboard Chart")
			chart.name = chart_data["name"]
			chart.chart_name = chart_data["chart_name"]
			chart.document_type = chart_data["document_type"]
			chart.chart_type = chart_data["chart_type"]
			chart.group_by_type = chart_data["group_by_type"]
			chart.group_by_based_on = chart_data["group_by_based_on"]
			chart.type = chart_data["type"]
			chart.filters_json = chart_data["filters_json"]
			chart.is_standard = 0
			chart.module = "Asset Tracker"
			chart.insert(ignore_permissions=True)


def setup_workspace():
	workspace_name = "Asset Tracker"
	if not frappe.db.exists("Workspace", workspace_name):
		ws = frappe.new_doc("Workspace")
		ws.name = workspace_name
		ws.title = workspace_name
		ws.label = workspace_name
		ws.category = "Modules"
		ws.icon = "box"
		ws.module = "Asset Tracker"
		ws.is_standard = 0
		ws.public = 1

		# Shortcuts
		ws.append(
			"shortcuts",
			{
				"type": "DocType",
				"link_to": "Asset",
				"label": "Assets",
				"doc_view": "List",
			},
		)
		ws.append(
			"shortcuts",
			{
				"type": "DocType",
				"link_to": "Asset Assignment",
				"label": "Asset Assignments",
				"doc_view": "List",
			},
		)
		ws.append(
			"shortcuts",
			{
				"type": "DocType",
				"link_to": "Asset Maintenance",
				"label": "Maintenance",
				"doc_view": "List",
			},
		)
		ws.append(
			"shortcuts",
			{
				"type": "DocType",
				"link_to": "Asset Category",
				"label": "Categories",
				"doc_view": "List",
			},
		)
		ws.append(
			"shortcuts",
			{
				"type": "Report",
				"link_to": "Asset Register",
				"label": "Asset Register Report",
			},
		)

		# Number Cards
		for card in ["Total Assets", "Total Asset Valuation", "Active Assignments", "Maintenance Due Soon"]:
			if frappe.db.exists("Number Card", card):
				ws.append("number_cards", {"number_card_name": card, "label": card})

		# Charts
		for chart in ["Assets by Status", "Assets by Category"]:
			if frappe.db.exists("Dashboard Chart", chart):
				ws.append("charts", {"chart_name": chart, "label": chart})

		ws.insert(ignore_permissions=True)
