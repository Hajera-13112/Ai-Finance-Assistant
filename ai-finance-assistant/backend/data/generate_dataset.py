"""
Generates a synthetic but realistic transaction dataset for training the
expense classifier, as required by SRS section 14 (Dataset Requirements).
"""
import csv
import random
import datetime as dt

random.seed(42)

TEMPLATES = {
    "Food": [
        "swiggy dinner {amt}", "zomato lunch order {amt}", "dominos pizza {amt}",
        "starbucks coffee {amt}", "restaurant bill {amt}", "grocery store bigbasket {amt}",
        "mcdonalds meal {amt}", "cafe coffee day {amt}", "street food vendor {amt}",
        "supermarket vegetables {amt}", "bakery order {amt}", "food delivery {amt}",
    ],
    "Transport": [
        "uber ride {amt}", "ola cab {amt}", "petrol pump fuel {amt}", "metro card recharge {amt}",
        "bus ticket {amt}", "train ticket irctc {amt}", "parking fee {amt}", "rapido bike {amt}",
        "toll payment fastag {amt}", "car service {amt}", "auto rickshaw fare {amt}",
    ],
    "Shopping": [
        "amazon order {amt}", "flipkart purchase {amt}", "myntra clothes {amt}",
        "shopping mall {amt}", "electronics store {amt}", "footwear purchase {amt}",
        "ajio order {amt}", "decathlon sports gear {amt}", "furniture store {amt}",
    ],
    "Bills": [
        "electricity bill payment {amt}", "water bill {amt}", "mobile recharge jio {amt}",
        "broadband internet bill {amt}", "gas cylinder booking {amt}", "rent payment {amt}",
        "credit card bill payment {amt}", "dth recharge {amt}", "maintenance society bill {amt}",
    ],
    "Entertainment": [
        "netflix subscription {amt}", "movie tickets bookmyshow {amt}", "spotify premium {amt}",
        "amazon prime subscription {amt}", "gaming purchase steam {amt}", "concert tickets {amt}",
        "amusement park entry {amt}", "hotstar subscription {amt}",
    ],
    "Health": [
        "pharmacy medicines {amt}", "doctor consultation fee {amt}", "hospital bill {amt}",
        "gym membership fee {amt}", "health insurance premium {amt}", "dental checkup {amt}",
        "diagnostic lab test {amt}", "yoga class fee {amt}",
    ],
    "Education": [
        "online course udemy {amt}", "college tuition fee {amt}", "book purchase {amt}",
        "coaching class fee {amt}", "exam registration fee {amt}", "school fees payment {amt}",
        "coursera subscription {amt}",
    ],
    "Other": [
        "cash withdrawal atm {amt}", "miscellaneous expense {amt}", "gift purchase {amt}",
        "donation charity {amt}", "bank service charge {amt}", "salon haircut {amt}",
        "pet supplies {amt}", "home repair {amt}",
    ],
}

AMOUNT_RANGES = {
    "Food": (80, 1200), "Transport": (30, 2500), "Shopping": (200, 8000),
    "Bills": (150, 6000), "Entertainment": (99, 1500), "Health": (150, 5000),
    "Education": (300, 15000), "Other": (50, 3000),
}

rows = []
tx_id = 1
start_date = dt.date(2025, 1, 1)

for day_offset in range(365):
    date = start_date + dt.timedelta(days=day_offset)
    num_tx = random.randint(0, 4)
    for _ in range(num_tx):
        category = random.choice(list(TEMPLATES.keys()))
        template = random.choice(TEMPLATES[category])
        low, high = AMOUNT_RANGES[category]
        amount = round(random.uniform(low, high), 2)
        description = template.format(amt=int(amount))
        rows.append({
            "transaction_id": tx_id,
            "date": date.isoformat(),
            "description": description,
            "amount": amount,
            "transaction_type": "expense",
            "category": category,
            "merchant": description.split(" ")[0],
        })
        tx_id += 1

with open("sample_transactions.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "transaction_id", "date", "description", "amount",
        "transaction_type", "category", "merchant",
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} transactions -> sample_transactions.csv")
