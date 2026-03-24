import os
import json
import pandas as pd

def load_json_folder(fp):
    data = []
    for file in os.listdir(fp):
        if file.endswith(".jsonl"):
            with open(os.path.join(fp, file)) as f:
                for line in f:
                    data.append(json.loads(line))
    return pd.DataFrame(data)


base = "/Users/triahavijayekkumaran/Downloads/dodge/sap-o2c-data"

sales_orders = load_json_folder(f"{base}/sales_order_headers")
sales_items = load_json_folder(f"{base}/sales_order_items")

delivery_items = load_json_folder(f"{base}/outbound_delivery_items")
billing_items = load_json_folder(f"{base}/billing_document_items")

journal = load_json_folder(f"{base}/journal_entry_items_accounts_receivable")
payments = load_json_folder(f"{base}/payments_accounts_receivable")

def standardize_columns(df):
    df.columns = [col.lower() for col in df.columns]
    return df

sales_orders = standardize_columns(sales_orders)
sales_items = standardize_columns(sales_items)
delivery_items = standardize_columns(delivery_items)
billing_items = standardize_columns(billing_items)
journal = standardize_columns(journal)
payments = standardize_columns(payments)

sales_items = sales_items.dropna(subset=['salesorder'])
delivery_items = delivery_items.dropna(subset=['referencesddocument'])
billing_items = billing_items.dropna(subset=['referencesddocument'])
journal = journal.dropna(subset=['referencedocument'])
payments = payments.dropna(subset=['accountingdocument'])

sales_items['salesorder'] = sales_items['salesorder'].astype(str)
sales_items['salesorderitem'] = sales_items['salesorderitem'].astype(str)

delivery_items['referencesddocument'] = delivery_items['referencesddocument'].astype(str)
delivery_items['deliverydocument'] = delivery_items['deliverydocument'].astype(str)
delivery_items['deliverydocumentitem'] = delivery_items['deliverydocumentitem'].astype(str)

billing_items['referencesddocument'] = billing_items['referencesddocument'].astype(str)
billing_items['billingdocument'] = billing_items['billingdocument'].astype(str)
billing_items['billingdocumentitem'] = billing_items['billingdocumentitem'].astype(str)

journal['referencedocument'] = journal['referencedocument'].astype(str)
journal['accountingdocument'] = journal['accountingdocument'].astype(str)

payments['accountingdocument'] = payments['accountingdocument'].astype(str)

sales_items = sales_items.drop_duplicates()
delivery_items = delivery_items.drop_duplicates()
billing_items = billing_items.drop_duplicates()
journal = journal.drop_duplicates()
payments = payments.drop_duplicates()

print("\n--- JOIN VALIDATION ---")
print("Order → Delivery:", sales_items['salesorder'].isin(delivery_items['referencesddocument']).sum())
print("Delivery → Billing:", delivery_items['deliverydocument'].isin(billing_items['referencesddocument']).sum())
print("Billing → Journal:", billing_items['billingdocument'].isin(journal['referencedocument']).sum())
print("Journal → Payment:", journal['accountingdocument'].isin(payments['accountingdocument']).sum())

sales_items['node_id'] = "SO_" + sales_items['salesorder'] + "_" + sales_items['salesorderitem']
delivery_items['node_id'] = "DL_" + delivery_items['deliverydocument'] + "_" + delivery_items['deliverydocumentitem']
billing_items['node_id'] = "BL_" + billing_items['billingdocument'] + "_" + billing_items['billingdocumentitem']
journal['node_id'] = "JE_" + journal['accountingdocument']
payments['node_id'] = "PY_" + payments['accountingdocument']

print("\n--- DATA SHAPES ---")
print("Sales Items:", sales_items.shape)
print("Delivery Items:", delivery_items.shape)
print("Billing Items:", billing_items.shape)
print("Journal:", journal.shape)
print("Payments:", payments.shape)

sales_items.to_csv("clean_sales_items.csv", index=False)
delivery_items.to_csv("clean_delivery_items.csv", index=False)
billing_items.to_csv("clean_billing_items.csv", index=False)
journal.to_csv("clean_journal.csv", index=False)
payments.to_csv("clean_payments.csv", index=False)

print(sales_items['node_id'].nunique())
print(delivery_items['node_id'].nunique())

print("\n✅ Phase 1 completed successfully!")
