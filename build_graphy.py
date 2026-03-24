import pandas as pd
import networkx as nx

sales_items = pd.read_csv("clean_sales_items.csv")
delivery_items = pd.read_csv("clean_delivery_items.csv")
billing_items = pd.read_csv("clean_billing_items.csv")
journal = pd.read_csv("clean_journal.csv")
payments = pd.read_csv("clean_payments.csv")

G = nx.DiGraph()


for _, row in sales_items.iterrows():
    G.add_node(
        row['node_id'],
        type="order",
        salesorder=row['salesorder'],
        item=row['salesorderitem'],
        material=row['material'],
        amount=row['netamount']
    )

for _, row in delivery_items.iterrows():
    G.add_node(
        row['node_id'],
        type="delivery",
        deliverydocument=row['deliverydocument'],
        item=row['deliverydocumentitem'],
        plant=row['plant']
    )

for _, row in billing_items.iterrows():
    G.add_node(
        row['node_id'],
        type="invoice",
        billingdocument=row['billingdocument'],
        item=row['billingdocumentitem'],
        amount=row['netamount']
    )

for _, row in journal.iterrows():
    G.add_node(
        row['node_id'],
        type="journal",
        accountingdocument=row['accountingdocument'],
        amount=row['amountintransactioncurrency']
    )

for _, row in payments.iterrows():
    G.add_node(
        row['node_id'],
        type="payment",
        accountingdocument=row['accountingdocument'],
        amount=row['amountintransactioncurrency']
    )


for _, d_row in delivery_items.iterrows():
    so = d_row['referencesddocument']
    matching_orders = sales_items[sales_items['salesorder'] == so]

    for _, s_row in matching_orders.iterrows():
        G.add_edge(s_row['node_id'], d_row['node_id'], type="order_to_delivery")

for _, b_row in billing_items.iterrows():
    dl = b_row['referencesddocument']
    matching_deliveries = delivery_items[delivery_items['deliverydocument'] == dl]

    for _, d_row in matching_deliveries.iterrows():
        G.add_edge(d_row['node_id'], b_row['node_id'], type="delivery_to_invoice")

for _, j_row in journal.iterrows():
    bill = j_row['referencedocument']
    matching_billing = billing_items[billing_items['billingdocument'] == bill]

    for _, b_row in matching_billing.iterrows():
        G.add_edge(b_row['node_id'], j_row['node_id'], type="invoice_to_journal")

for _, p_row in payments.iterrows():
    acc = p_row['accountingdocument']
    matching_journal = journal[journal['accountingdocument'] == acc]

    for _, j_row in matching_journal.iterrows():
        G.add_edge(j_row['node_id'], p_row['node_id'], type="journal_to_payment")


print("\n--- GRAPH SUMMARY ---")
print("Total Nodes:", G.number_of_nodes())
print("Total Edges:", G.number_of_edges())


def find_complete_flow():
    for _, s_row in sales_items.iterrows():
        so_node = s_row['node_id']

        d = list(G.successors(so_node))
        if not d:
            continue

        b = []
        for x in d:
            b.extend(list(G.successors(x)))
        if not b:
            continue

        j = []
        for x in b:
            j.extend(list(G.successors(x)))
        if not j:
            continue

        p = []
        for x in j:
            p.extend(list(G.successors(x)))
        if not p:
            continue

        return so_node

    return None


sample_order = find_complete_flow()

if sample_order:
    print("\nTracing COMPLETE flow for:", sample_order)

    level1 = list(G.successors(sample_order))
    print("→ Delivery:", level1)

    level2 = []
    for n in level1:
        level2.extend(list(G.successors(n)))
    print("→ Billing:", level2)

    level3 = []
    for n in level2:
        level3.extend(list(G.successors(n)))
    print("→ Journal:", level3)

    level4 = []
    for n in level3:
        level4.extend(list(G.successors(n)))
    print("→ Payment:", level4)

else:
    print("\n⚠️ No complete flow found in dataset")



def get_full_flow(order_node):
    flow = {
        "order": order_node,
        "deliveries": [],
        "billing": [],
        "journal": [],
        "payments": []
    }

    deliveries = list(G.successors(order_node))
    flow["deliveries"] = deliveries

    billing = []
    for d in deliveries:
        billing.extend(list(G.successors(d)))
    flow["billing"] = billing

    journal_list = []
    for b in billing:
        journal_list.extend(list(G.successors(b)))
    flow["journal"] = journal_list

    payments_list = []
    for j in journal_list:
        payments_list.extend(list(G.successors(j)))
    flow["payments"] = payments_list

    return flow


def get_highest_billing_products(top_n=5):
    df = billing_items.copy()

    grouped = (
        df.groupby("material")["netamount"]
        .sum()
        .sort_values(ascending=False)
    )

    return grouped.head(top_n)


def find_incomplete_orders():
    incomplete = []

    for _, row in sales_items.iterrows():
        node = row['node_id']

        deliveries = list(G.successors(node))
        if not deliveries:
            incomplete.append((node, "no_delivery"))
            continue

        billing = []
        for d in deliveries:
            billing.extend(list(G.successors(d)))
        if not billing:
            incomplete.append((node, "no_billing"))
            continue

        journal_list = []
        for b in billing:
            journal_list.extend(list(G.successors(b)))
        if not journal_list:
            incomplete.append((node, "no_journal"))
            continue

        payments_list = []
        for j in journal_list:
            payments_list.extend(list(G.successors(j)))
        if not payments_list:
            incomplete.append((node, "no_payment"))
            continue

    return incomplete


print("\n--- FULL FLOW QUERY ---")
if sample_order:
    print(get_full_flow(sample_order))

print("\n--- TOP PRODUCTS ---")
print(get_highest_billing_products())

print("\n--- INCOMPLETE ORDERS ---")
print(find_incomplete_orders()[:10])
