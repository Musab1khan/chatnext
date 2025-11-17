#!/usr/bin/env python3
"""
Load default proactive rules for Chatnext
Pre-configured rules for common business scenarios
"""

import frappe

def load_proactive_rules():
    """Load all default proactive rules"""

    rules = get_default_rules()

    created_count = 0
    skipped_count = 0

    for rule_data in rules:
        try:
            # Check if already exists
            if frappe.db.exists("Proactive Rule", rule_data["rule_name"]):
                print(f"⚠️  {rule_data['rule_name']} already exists, skipping...")
                skipped_count += 1
                continue

            # Create rule
            rule = frappe.get_doc({
                "doctype": "Proactive Rule",
                **rule_data
            })
            rule.insert(ignore_permissions=True)
            frappe.db.commit()

            print(f"✅ Created: {rule_data['rule_name']}")
            created_count += 1

        except Exception as e:
            print(f"❌ Error creating {rule_data.get('rule_name', 'Unknown')}: {str(e)}")
            frappe.db.rollback()

    print(f"\n✅ Proactive Rules loaded successfully!")
    print(f"   Created: {created_count} rules")
    print(f"   Skipped: {skipped_count} rules")

def get_default_rules():
    """Return list of default proactive rules"""

    return [
        {
            "rule_name": "Low Stock Alert",
            "description": "Alert when items fall below reorder level",
            "rule_type": "Low Stock Alert",
            "target_doctype": "Bin",
            "condition": "actual_qty <= reorder_level and reorder_level > 0",
            "suggestion_template": """<p><strong>⚠️ Low Stock Alert</strong></p>
<p>Some items have fallen below their reorder levels. You should create Purchase Orders to restock.</p>
<p><strong>Action:</strong> Go to <em>Stock → Stock Reports → Stock Balance</em> to view items needing reorder.</p>""",
            "suggestion_template_urdu": """<p><strong>⚠️ کم اسٹاک کی انتباہ</strong></p>
<p>کچھ items اپنے reorder level سے نیچے آ گئے ہیں۔ آپ کو دوبارہ اسٹاک کرنے کے لیے Purchase Orders بنانے چاہیئیں۔</p>
<p><strong>ایکشن:</strong> <em>Stock → Stock Reports → Stock Balance</em> پر جائیں اور reorder کی ضرورت والے items دیکھیں۔</p>""",
            "priority": "High",
            "frequency": "Daily",
            "is_active": 1
        },
        {
            "rule_name": "Overdue Invoices",
            "description": "Notify about overdue customer invoices",
            "rule_type": "Overdue Invoice",
            "target_doctype": "Sales Invoice",
            "condition": "due_date < today() and outstanding_amount > 0 and docstatus == 1",
            "suggestion_template": """<p><strong>💰 Overdue Invoices Alert</strong></p>
<p>You have invoices that are past their due date with outstanding payments.</p>
<p><strong>Action:</strong> Go to <em>Accounting → Accounts Receivable</em> to view and follow up on overdue invoices.</p>""",
            "suggestion_template_urdu": """<p><strong>💰 واجب الادا انوائسز کی انتباہ</strong></p>
<p>آپ کے پاس ایسے invoices ہیں جن کی due date گزر گئی ہے اور ادائیگی باقی ہے۔</p>
<p><strong>ایکشن:</strong> <em>Accounting → Accounts Receivable</em> پر جا کر overdue invoices دیکھیں اور follow up کریں۔</p>""",
            "priority": "Critical",
            "frequency": "Daily",
            "is_active": 1
        },
        {
            "rule_name": "Pending Leave Approvals",
            "description": "Remind about pending leave applications",
            "rule_type": "Missing Document",
            "target_doctype": "Leave Application",
            "condition": "workflow_state == 'Pending' and docstatus == 0",
            "suggestion_template": """<p><strong>📋 Pending Leave Approvals</strong></p>
<p>There are leave applications waiting for your approval.</p>
<p><strong>Action:</strong> Go to <em>HR → Leave Application</em> and review pending requests.</p>""",
            "suggestion_template_urdu": """<p><strong>📋 زیر التواء چھٹی کی منظوریاں</strong></p>
<p>آپ کی منظوری کے منتظر leave applications ہیں۔</p>
<p><strong>ایکشن:</strong> <em>HR → Leave Application</em> پر جا کر pending requests کا جائزہ لیں۔</p>""",
            "priority": "Medium",
            "frequency": "Daily",
            "is_active": 1
        },
        {
            "rule_name": "Expiring Contracts",
            "description": "Alert about contracts expiring within 30 days",
            "rule_type": "Expiring Contract",
            "target_doctype": "Contract",
            "condition": "end_date <= add_days(today(), 30) and end_date >= today() and is_signed == 1",
            "suggestion_template": """<p><strong>📄 Expiring Contracts</strong></p>
<p>Some contracts are expiring within the next 30 days. Review and renew if necessary.</p>
<p><strong>Action:</strong> Check <em>CRM → Contract</em> for expiring contracts.</p>""",
            "suggestion_template_urdu": """<p><strong>📄 ختم ہوتے معاہدے</strong></p>
<p>کچھ contracts اگلے 30 دنوں میں ختم ہو رہے ہیں۔ ضرورت ہو تو renew کریں۔</p>
<p><strong>ایکشن:</strong> <em>CRM → Contract</em> میں expiring contracts چیک کریں۔</p>""",
            "priority": "High",
            "frequency": "Weekly",
            "is_active": 1
        },
        {
            "rule_name": "Unapproved Purchase Orders",
            "description": "Remind about draft purchase orders",
            "rule_type": "Missing Document",
            "target_doctype": "Purchase Order",
            "condition": "docstatus == 0 and creation < add_days(now(), -2)",
            "suggestion_template": """<p><strong>📦 Unapproved Purchase Orders</strong></p>
<p>You have draft Purchase Orders that haven't been submitted for more than 2 days.</p>
<p><strong>Action:</strong> Review and submit pending POs in <em>Buying → Purchase Order</em>.</p>""",
            "suggestion_template_urdu": """<p><strong>📦 غیر منظور شدہ Purchase Orders</strong></p>
<p>آپ کے draft Purchase Orders ہیں جو 2 دن سے زیادہ سے submit نہیں ہوئے۔</p>
<p><strong>ایکشن:</strong> <em>Buying → Purchase Order</em> میں pending POs کا جائزہ لے کر submit کریں۔</p>""",
            "priority": "Medium",
            "frequency": "Daily",
            "is_active": 1
        }
    ]

if __name__ == "__main__":
    load_proactive_rules()
