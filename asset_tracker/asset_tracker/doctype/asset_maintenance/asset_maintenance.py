# Copyright (c) 2026, Pragati Hegde and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate, today


class AssetMaintenance(Document):
	def validate(self):
		self.validate_disposed_asset()
		self.validate_dates()

	def validate_disposed_asset(self):
		asset_status = frappe.db.get_value("Asset", self.asset, "status")
		if asset_status == "Disposed":
			frappe.throw(f"Asset {self.asset} is disposed and cannot be scheduled for maintenance.")

	def validate_dates(self):
		if self.status == "Completed" and not self.completion_date:
			self.completion_date = today()

	def on_update(self):
		self.sync_asset_maintenance_status()

	def sync_asset_maintenance_status(self):
		if self.status == "In Progress":
			frappe.db.set_value("Asset", self.asset, "status", "Under Maintenance")
		elif self.status == "Completed":
			frappe.db.set_value("Asset", self.asset, "last_maintenance_date", self.completion_date)

			# Restore asset status
			active_assignment = frappe.db.get_value(
				"Asset Assignment",
				{"asset": self.asset, "status": "Active"},
				"name",
			)
			new_status = "Assigned" if active_assignment else "Available"
			frappe.db.set_value("Asset", self.asset, "status", new_status)

		# Update next scheduled maintenance date on asset
		next_scheduled = frappe.db.get_value(
			"Asset Maintenance",
			{
				"asset": self.asset,
				"status": "Scheduled",
				"scheduled_date": [">=", today()],
			},
			"scheduled_date",
			order_by="scheduled_date asc",
		)
		frappe.db.set_value("Asset", self.asset, "next_maintenance_date", next_scheduled)


def send_maintenance_alerts():
	"""
	Scheduled task (Daily):
	Checks for maintenance due within 7 days.
	Fires alert once per upcoming maintenance event (alert_sent flag prevents duplicate notifications).
	"""
	current_today = getdate(today())
	window_end = getdate(add_days(today(), 7))

	upcoming_maintenances = frappe.get_all(
		"Asset Maintenance",
		filters={
			"status": "Scheduled",
			"alert_sent": 0,
			"scheduled_date": ["between", [current_today, window_end]],
		},
		fields=["name", "asset", "maintenance_type", "scheduled_date"],
	)

	if not upcoming_maintenances:
		return

	# Retrieve users with 'Asset Manager' or 'System Manager' role
	asset_managers = frappe.get_all(
		"Has Role",
		filters={"role": ["in", ["Asset Manager", "System Manager"]], "parenttype": "User"},
		pluck="parent",
		distinct=True,
	)

	for m in upcoming_maintenances:
		asset_name = frappe.db.get_value("Asset", m.asset, "asset_name") or m.asset
		subject = f"Maintenance Alert: Asset {m.asset} ({asset_name}) due on {m.scheduled_date}"
		message = (
			f"Scheduled maintenance of type <b>{m.maintenance_type}</b> for asset <b>{m.asset} - {asset_name}</b> "
			f"is due within 7 days on <b>{m.scheduled_date}</b>.<br>"
			f"Maintenance ID: <a href='/app/asset-maintenance/{m.name}'>{m.name}</a>"
		)

		for user in asset_managers:
			if user in ["Administrator", "Guest"]:
				continue

			try:
				# Create desk notification
				notification = frappe.new_doc("Notification Log")
				notification.subject = subject
				notification.email_content = message
				notification.for_user = user
				notification.document_type = "Asset Maintenance"
				notification.document_name = m.name
				notification.insert(ignore_permissions=True)
			except Exception:
				frappe.log_error(title="Failed to dispatch asset maintenance notification")

		# Mark alert_sent = 1 so this alert never fires repeatedly
		frappe.db.set_value("Asset Maintenance", m.name, "alert_sent", 1, update_modified=False)

	frappe.db.commit()
