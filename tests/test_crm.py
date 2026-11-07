
import json
import uuid
import urllib.request
import urllib.error

URL = "http://localhost:5678/webhook/crm-new-lead"

def submit_lead(lead):
    payload = json.dumps(lead).encode("utf-8")

    request = urllib.request.Request(
        URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            body = response.read().decode()
            return response.status, json.loads(body)

    except urllib.error.HTTPError as error:
        body = error.read().decode()
        return error.code, json.loads(body)


def test(name, condition):
    print(f"{'PASS' if condition else 'FAIL'} - {name}")
    return bool(condition)


run_id = str(uuid.uuid4())[:8]
event_id = "EVENT-" + str(uuid.uuid4())
email = f"crm-test-{run_id}@example.com"

valid_lead = {
    "event_id": event_id,
    "lead_id": "LEAD-" + run_id,
    "name": "Test Customer",
    "email": email,
    "phone": "+15550100999",
    "company": "Test Automation Agency",
    "service": "CRM Automation",
    "budget": 3000,
    "timeline": "Within 30 days",
    "message": "We need AI lead qualification automation.",
    "source": "automated_test"
}

results = []

print("\nTEST 1 - VALID LEAD")
status1, body1 = submit_lead(valid_lead)

results.append(test(
    "Returns HTTP 200",
    status1 == 200
))

results.append(test(
    "Lead processed successfully",
    body1.get("success") is True
    and body1.get("duplicate") is False
))

results.append(test(
    "HubSpot contact ID exists",
    bool(body1.get("crm", {}).get("contact_id"))
))

print("\nTEST 2 - DUPLICATE EVENT")
status2, body2 = submit_lead(valid_lead)

results.append(test(
    "Duplicate receives HTTP 200",
    status2 == 200
))

results.append(test(
    "Duplicate detected",
    body2.get("duplicate") is True
))

print("\nTEST 3 - INVALID EMAIL")
invalid_lead = {
    **valid_lead,
    "event_id": "EVENT-" + str(uuid.uuid4()),
    "email": "invalid-email"
}

status3, body3 = submit_lead(invalid_lead)

results.append(test(
    "Invalid email returns HTTP 400",
    status3 == 400
))

results.append(test(
    "Validation error returned",
    body3.get("error") == "VALIDATION_FAILED"
))

print("\nTEST 4 - NEW EVENT, SAME CUSTOMER")
updated_lead = {
    **valid_lead,
    "event_id": "EVENT-" + str(uuid.uuid4()),
    "budget": 5000,
    "message": "We increased our budget."
}

status4, body4 = submit_lead(updated_lead)

results.append(test(
    "Updated inquiry returns HTTP 200",
    status4 == 200
))

results.append(test(
    "Not treated as duplicate",
    body4.get("duplicate") is False
))

first_id = body1.get("crm", {}).get("contact_id")
updated_id = body4.get("crm", {}).get("contact_id")

results.append(test(
    "Same HubSpot contact ID",
    first_id is not None and first_id == updated_id
))

print("\nFINAL REPORT")
print(f"Passed: {sum(results)}/{len(results)}")
print(f"Failed: {len(results) - sum(results)}")

if not all(results):
    raise SystemExit(1)
