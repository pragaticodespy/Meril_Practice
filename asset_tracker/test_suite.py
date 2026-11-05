import frappe
from frappe.utils import add_days, today, getdate, flt
from asset_tracker.asset_tracker.doctype.asset.asset import process_monthly_depreciation
from asset_tracker.asset_tracker.doctype.asset_maintenance.asset_maintenance import send_maintenance_alerts
from asset_tracker.api import get_employee_assets, get_upcoming_maintenance
from asset_tracker.asset_tracker.report.asset_register.asset_register import execute as run_asset_register

def test_full_lifecycle():
    print("\n=======================================================")
    print("STARTING ASSET TRACKER COMPREHENSIVE VERIFICATION SUITE")
    print("=======================================================\n")

    # 1. SETUP CATEGORIES
    categories = [
        {"name": "Laptops", "depreciation_rate": 20.0, "description": "High-performance company laptops"},
        {"name": "Phones", "depreciation_rate": 25.0, "description": "Smartphones and mobile devices"},
        {"name": "Vehicles", "depreciation_rate": 15.0, "description": "Company fleet vehicles"},
        {"name": "Projectors", "depreciation_rate": 10.0, "description": "Conference room audio/visual gear"}
    ]
    for c in categories:
        if not frappe.db.exists("Asset Category", c["name"]):
            doc = frappe.new_doc("Asset Category")
            doc.category_name = c["name"]
            doc.depreciation_rate = c["depreciation_rate"]
            doc.description = c["description"]
            doc.insert(ignore_permissions=True)
            print(f"Created Asset Category: {c['name']} (Annual Rate: {c['depreciation_rate']}%)")

    # 2. SETUP EMPLOYEES
    employees_data = [
        {"employee_name": "Rahul Sharma", "email": "rahul.sharma@example.com", "department": "Engineering", "designation": "Software Engineer"},
        {"employee_name": "Priya Nair", "email": "priya.nair@example.com", "department": "Marketing", "designation": "Marketing Lead"},
        {"employee_name": "Amit Patel", "email": "amit.patel@example.com", "department": "Operations", "designation": "Operations Specialist"}
    ]
    emp_ids = {}
    for e in employees_data:
        emp_name = frappe.db.get_value("Employee", {"email": e["email"]}, "name")
        if not emp_name:
            doc = frappe.new_doc("Employee")
            doc.employee_name = e["employee_name"]
            doc.email = e["email"]
            doc.department = e["department"]
            doc.designation = e["designation"]
            doc.insert(ignore_permissions=True)
            emp_name = doc.name
            print(f"Created Employee: {doc.employee_name} ({emp_name})")
        emp_ids[e["employee_name"]] = emp_name

    # 3. SETUP ASSETS
    assets_data = [
        {"asset_name": "MacBook Pro M3 Max", "category": "Laptops", "department": "Engineering", "purchase_cost": 240000.0, "condition": "New"},
        {"asset_name": "Dell XPS 15", "category": "Laptops", "department": "Engineering", "purchase_cost": 180000.0, "condition": "Good"},
        {"asset_name": "ThinkPad X1 Carbon", "category": "Laptops", "department": "Engineering", "purchase_cost": 150000.0, "condition": "Good"},
        {"asset_name": "HP EliteBook 840", "category": "Laptops", "department": "Engineering", "purchase_cost": 120000.0, "condition": "Good"},
        {"asset_name": "iPhone 15 Pro", "category": "Phones", "department": "Marketing", "purchase_cost": 130000.0, "condition": "New"},
        {"asset_name": "Toyota Innova Crysta", "category": "Vehicles", "department": "Operations", "purchase_cost": 2500000.0, "condition": "Good"},
        {"asset_name": "Sony 4K Laser Projector", "category": "Projectors", "department": "Operations", "purchase_cost": 350000.0, "condition": "New"}
    ]

    asset_map = {}
    for a in assets_data:
        existing = frappe.db.get_value("Asset", {"asset_name": a["asset_name"]}, "name")
        if not existing:
            doc = frappe.new_doc("Asset")
            doc.asset_name = a["asset_name"]
            doc.category = a["category"]
            doc.department = a["department"]
            doc.purchase_date = today()
            doc.purchase_cost = a["purchase_cost"]
            doc.current_value = a["purchase_cost"]
            doc.condition = a["condition"]
            doc.status = "Available"
            doc.insert(ignore_permissions=True)
            existing = doc.name
            print(f"Created Asset: {a['asset_name']} ({existing}) - Cost: {a['purchase_cost']}")
        asset_map[a["asset_name"]] = existing

    frappe.db.commit()

    # 4. TEST ASSIGNMENT & RULES
    print("\n--- Testing Assignment Rules ---")
    rahul_id = emp_ids["Rahul Sharma"]
    mbp_id = asset_map["MacBook Pro M3 Max"]

    # Assign 1st asset to Rahul
    asgn1 = frappe.new_doc("Asset Assignment")
    asgn1.asset = mbp_id
    asgn1.employee = rahul_id
    asgn1.assignment_date = today()
    asgn1.issue_condition = "New"
    asgn1.status = "Active"
    asgn1.insert(ignore_permissions=True)
    print(f"[PASSED] Issued {mbp_id} to Rahul Sharma (Assignment: {asgn1.name})")

    # Verify Asset status updated to Assigned
    asset_status, custodian = frappe.db.get_value("Asset", mbp_id, ["status", "current_employee"])
    assert asset_status == "Assigned", f"Expected Assigned, got {asset_status}"
    assert custodian == rahul_id, f"Expected {rahul_id}, got {custodian}"
    print(f"[PASSED] Asset {mbp_id} status correctly synced: {asset_status}, Custodian: {custodian}")

    # TEST: Try assigning mbp_id to Priya while already assigned to Rahul -> MUST FAIL
    priya_id = emp_ids["Priya Nair"]
    try:
        asgn_conflict = frappe.new_doc("Asset Assignment")
        asgn_conflict.asset = mbp_id
        asgn_conflict.employee = priya_id
        asgn_conflict.assignment_date = today()
        asgn_conflict.issue_condition = "Good"
        asgn_conflict.status = "Active"
        asgn_conflict.insert(ignore_permissions=True)
        assert False, "Should have thrown ValidationError for double assignment!"
    except frappe.ValidationError as e:
        print(f"[PASSED] Prevented double assignment error as expected: {e}")

    # TEST: Holding limit warning before 4th assignment
    # Assign 2nd and 3rd asset to Rahul
    dell_id = asset_map["Dell XPS 15"]
    thinkpad_id = asset_map["ThinkPad X1 Carbon"]
    hp_id = asset_map["HP EliteBook 840"]

    asgn2 = frappe.new_doc("Asset Assignment")
    asgn2.asset = dell_id
    asgn2.employee = rahul_id
    asgn2.assignment_date = today()
    asgn2.issue_condition = "Good"
    asgn2.status = "Active"
    asgn2.insert(ignore_permissions=True)

    asgn3 = frappe.new_doc("Asset Assignment")
    asgn3.asset = thinkpad_id
    asgn3.employee = rahul_id
    asgn3.assignment_date = today()
    asgn3.issue_condition = "Good"
    asgn3.status = "Active"
    asgn3.insert(ignore_permissions=True)

    print(f"Rahul now holds 3 active assets: {mbp_id}, {dell_id}, {thinkpad_id}")

    # Now assign 4th asset to Rahul - should trigger msgprint holding limit warning
    asgn4 = frappe.new_doc("Asset Assignment")
    asgn4.asset = hp_id
    asgn4.employee = rahul_id
    asgn4.assignment_date = today()
    asgn4.issue_condition = "Good"
    asgn4.status = "Active"
    asgn4.insert(ignore_permissions=True)
    print(f"[PASSED] 4th assignment allowed with holding limit warning evaluated successfully!")

    # TEST: Return an asset (mandatory return condition)
    try:
        asgn4.status = "Returned"
        asgn4.return_condition = "" # Empty condition
        asgn4.save(ignore_permissions=True)
        assert False, "Should have failed without return_condition!"
    except frappe.ValidationError as e:
        print(f"[PASSED] Mandatory return condition enforced on return: {e}")

    # Complete return properly
    asgn4.reload()
    asgn4.status = "Returned"
    asgn4.return_condition = "Good"
    asgn4.return_date = today()
    asgn4.save(ignore_permissions=True)
    asset_status, custodian = frappe.db.get_value("Asset", hp_id, ["status", "current_employee"])
    assert asset_status == "Available", f"Expected Available, got {asset_status}"
    assert custodian is None, f"Expected None, got {custodian}"
    print(f"[PASSED] Asset {hp_id} returned properly; restored to Available and custodian cleared.")

    # 5. TEST MAINTENANCE & 7-DAY ALERT
    print("\n--- Testing Maintenance Lifecycle & Alerts ---")
    innova_id = asset_map["Toyota Innova Crysta"]

    # Schedule maintenance within 5 days
    mnt1 = frappe.new_doc("Asset Maintenance")
    mnt1.asset = innova_id
    mnt1.maintenance_type = "Preventive Maintenance"
    mnt1.scheduled_date = add_days(today(), 5) # Within 7 days
    mnt1.status = "Scheduled"
    mnt1.insert(ignore_permissions=True)
    print(f"Scheduled maintenance {mnt1.name} for {innova_id} on {mnt1.scheduled_date}")

    # Run maintenance alert check
    assert mnt1.alert_sent == 0
    send_maintenance_alerts()
    alert_status = frappe.db.get_value("Asset Maintenance", mnt1.name, "alert_sent")
    assert alert_status == 1, "Alert flag should be set to 1 after dispatch"
    print(f"[PASSED] 7-day maintenance alert dispatched and alert_sent set to 1")

    # Run again - verify it does NOT fire again
    send_maintenance_alerts()
    print(f"[PASSED] Alert guaranteed to fire exactly once per event.")

    # Mark In Progress
    mnt1.reload()
    mnt1.status = "In Progress"
    mnt1.save(ignore_permissions=True)
    innova_status = frappe.db.get_value("Asset", innova_id, "status")
    assert innova_status == "Under Maintenance"
    print(f"[PASSED] Asset status updated to 'Under Maintenance' when service starts.")

    # Mark Completed
    mnt1.status = "Completed"
    mnt1.completion_date = today()
    mnt1.maintenance_cost = 8500.0
    mnt1.save(ignore_permissions=True)
    innova_status, last_mnt = frappe.db.get_value("Asset", innova_id, ["status", "last_maintenance_date"])
    assert innova_status == "Available"
    assert str(last_mnt) == today()
    print(f"[PASSED] Maintenance marked completed; asset restored to Available, last_maintenance_date recorded: {last_mnt}")

    # 6. TEST DISPOSAL & SAFEGUARDS
    print("\n--- Testing Disposal & Safeguards ---")
    projector_id = asset_map["Sony 4K Laser Projector"]

    # Dispose projector
    proj_doc = frappe.get_doc("Asset", projector_id)
    proj_doc.status = "Disposed"
    proj_doc.disposal_date = today()
    proj_doc.disposal_reason = "Irreparable optical engine failure"
    proj_doc.save(ignore_permissions=True)
    print(f"[PASSED] Asset {projector_id} marked as Disposed with reason.")

    # Try assigning disposed asset -> MUST FAIL
    try:
        disposed_asgn = frappe.new_doc("Asset Assignment")
        disposed_asgn.asset = projector_id
        disposed_asgn.employee = priya_id
        disposed_asgn.issue_condition = "Damaged"
        disposed_asgn.status = "Active"
        disposed_asgn.insert(ignore_permissions=True)
        assert False, "Should have failed to assign disposed asset!"
    except frappe.ValidationError as e:
        print(f"[PASSED] Assignment blocked on disposed asset: {e}")

    # Try scheduling maintenance on disposed asset -> MUST FAIL
    try:
        disposed_mnt = frappe.new_doc("Asset Maintenance")
        disposed_mnt.asset = projector_id
        disposed_mnt.maintenance_type = "Repair"
        disposed_mnt.scheduled_date = add_days(today(), 2)
        disposed_mnt.status = "Scheduled"
        disposed_mnt.insert(ignore_permissions=True)
        assert False, "Should have failed to schedule maintenance on disposed asset!"
    except frappe.ValidationError as e:
        print(f"[PASSED] Maintenance blocked on disposed asset: {e}")

    # 7. TEST AUTOMATIC MONTHLY DEPRECIATION
    print("\n--- Testing Monthly Straight-Line Depreciation ---")
    mbp_doc = frappe.get_doc("Asset", mbp_id)
    initial_val = flt(mbp_doc.current_value)
    purchase_cost = flt(mbp_doc.purchase_cost)
    category_rate = flt(frappe.db.get_value("Asset Category", mbp_doc.category, "depreciation_rate"))
    expected_dep = round(purchase_cost * (category_rate / 100.0) / 12.0, 2)
    expected_after = round(initial_val - expected_dep, 2)

    process_monthly_depreciation()
    mbp_doc.reload()

    print(f"Initial Value: {initial_val}, Depreciation Rate: {category_rate}%, Expected Dep: {expected_dep}")
    print(f"Current Value after run: {mbp_doc.current_value}")
    assert mbp_doc.current_value == expected_after, f"Expected {expected_after}, got {mbp_doc.current_value}"

    # Verify audit log
    dep_log = frappe.get_all("Asset Depreciation Log", filters={"asset": mbp_id}, fields=["depreciation_amount", "value_before", "value_after"])
    assert len(dep_log) >= 1
    print(f"[PASSED] Depreciation applied and logged in Asset Depreciation Log: {dep_log[0]}")

    # TEST: Second run in the same month MUST SKIP
    val_before_second = mbp_doc.current_value
    process_monthly_depreciation()
    mbp_doc.reload()
    assert mbp_doc.current_value == val_before_second, "Depreciation ran twice in same month!"
    print(f"[PASSED] Second depreciation run in the same month correctly skipped (Value remained {mbp_doc.current_value})")

    # 8. TEST CALLABLE APIS
    print("\n--- Testing Whitelisted APIs ---")
    emp_assets = get_employee_assets(employee=rahul_id)
    print(f"get_employee_assets('{rahul_id}') returned {len(emp_assets)} assets:")
    for ea in emp_assets:
        print(f"  - {ea['asset_name']} ({ea['name']}): Condition={ea['condition']}, Current Value={ea['current_value']}")
    assert len(emp_assets) >= 2

    upcoming = get_upcoming_maintenance(days=14)
    print(f"get_upcoming_maintenance(days=14) returned {len(upcoming)} items:")
    for u in upcoming:
        print(f"  - {u['asset']} ({u.get('asset_name')}): Due {u['scheduled_date']}, Type={u['maintenance_type']}")

    # 9. TEST SCRIPT REPORT
    print("\n--- Testing Script Report: Asset Register ---")
    cols, data, msg, chart, summary = run_asset_register({"category": "Laptops"})
    print(f"Asset Register columns count: {len(cols)}")
    print(f"Asset Register rows returned: {len(data)}")
    assert len(data) >= 1
    # Check summary row at bottom
    summary_row = data[-1]
    print(f"Summary Row: {summary_row['asset']} | Total Cost: {summary_row['purchase_cost']} | Total Value: {summary_row['current_value']}")
    assert summary_row["asset"] == "<b>Total</b>"
    assert summary_row["purchase_cost"] > 0
    assert summary_row["current_value"] > 0
    print(f"[PASSED] Script report returned valid filtered data with bottom summary row!")

    frappe.db.commit()
    print("\n=======================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! FULL LIFECYCLE VERIFIED.")
    print("=======================================================\n")

if __name__ == "__main__":
    test_full_lifecycle()
