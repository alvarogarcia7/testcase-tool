import os
import xml.etree.ElementTree as ET
from xmlrpc.client import DateTime, _iso8601_format

from tcms_api import TCMS

username = os.environ.get("KIWI_TCMS_USERNAME")
password = os.environ.get("KIWI_TCMS_PASSWORD")
if not username or not password:
    raise Exception("Error: KIWI_TCMS_USERNAME and KIWI_TCMS_PASSWORD must be set")
client = TCMS(
    url="https://public.tenant.kiwitcms.org/xml-rpc/",
    username=username,
    password=password,
)
tcms = client.exec

# https://public.tenant.kiwitcms.org/plan/search/?product=13534
PRODUCT_ID = 13534  # change to your product
PLAN_ID = 13697  # change to your plan
CATEGORY_ID = 2  # change to your category
# https://public.tenant.kiwitcms.org/plan/13697/
TESTPLAN_ID = 13697  # change if attaching to a plan
FEATURE_1_DOWNLOAD_TEST_CASES = False
FEATURE_2_DOWNLOAD_TEST_PLANS = False
FEATURE_3_DOWNLOAD_TEST_RUNS = True


def convert_if_present(obj, key):
    if key in obj:
        obj[key] = str(obj[key])


# # ✅ 2. Download ALL Test Cases
# all_cases = tcms.TestCase.filter()
# print(f"Downloaded {len(all_cases)} cases")
import json

if FEATURE_1_DOWNLOAD_TEST_CASES:

    # all_cases is a list of dictionaries holding the full TCMS metadata.
    #
    # ✅ 3. Download Test Cases for a Specific Product
    cases = tcms.TestCase.filter({"plan": PLAN_ID})
    print(f"Found {len(cases)} cases for plan {PLAN_ID}")

    output = "exported_testcases.json"
    with open(output, "w") as f:
        for case in cases:
            convert_if_present(case, "create_date")
        json.dump(cases, f, indent=2)

    print(f"Saved to {output}")

if FEATURE_2_DOWNLOAD_TEST_PLANS:
    response = tcms.TestPlan.filter({"id": PLAN_ID})
    print(f"Downloaded {len(response)} cases from plan {PLAN_ID}")

    output = "exported_testplans.json"
    with open(output, "w") as f:
        for case in response:
            convert_if_present(case, "create_date")
        json.dump(response, f, indent=2)

    print(f"Saved to {output}")


if FEATURE_3_DOWNLOAD_TEST_RUNS:
    response = tcms.TestRun.filter({"plan": PLAN_ID})
    print(f"Downloaded {len(response)} test runs from plan {PLAN_ID}")

    output = "exported_testruns.json"
    with open(output, "w") as f:
        for case in response:
            convert_if_present(case, "start_date")
            convert_if_present(case, "stop_date")
        json.dump(response, f, indent=2)

    print(f"Saved to {output}")

# # ✅ 4. Download Test Cases belonging to a Test Plan
# #
# # This is the most common workflow.
#
# PLAN_ID = 123
#
#
# # ✅ 5. Download Test Cases from a Category
# CATEGORY_ID = 5
#
# category_cases = tcms.TestCase.filter(category=CATEGORY_ID)
# print(f"Downloaded {len(category_cases)} cases in category {CATEGORY_ID}")

# ✅ 6. Save downloaded test cases to a JSON file (recommended)

# # Optional: Export to CSV
# import csv
#
# with open("testcases.csv", "w", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerow(["case_id", "summary", "priority", "category", "status"])
#
#     for case in all_cases:
#         writer.writerow([case["case_id"], case["summary"], case["priority"], case["category"], case["case_status"]])
