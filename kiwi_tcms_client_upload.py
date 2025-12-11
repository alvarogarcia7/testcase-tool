import os
import pprint
import xml.etree.ElementTree as ET

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
CATEGORY_ID = 14657  # change to your category
# https://public.tenant.kiwitcms.org/plan/13697/
TESTPLAN_ID = 13697  # change if attaching to a plan

# --------------------------------------------------------------------------
# PARSE JUNIT XML
# --------------------------------------------------------------------------
tree = ET.parse("data_working/results.xml")
root = tree.getroot()

namespace = ""
if root.tag.startswith("{"):
    namespace = root.tag.split("}")[0] + "}"

testcases = root.findall(".//" + namespace + "testcase")

print(f"Found {len(testcases)} JUnit test cases")


# --------------------------------------------------------------------------
# UPLOAD EACH TEST CASE TO KIWI TCMS
# --------------------------------------------------------------------------
created_cases = []

for tc in testcases:
    name = tc.attrib.get("name")
    classname = tc.attrib.get("classname", "")

    # Extract failure/error if exists — useful for expected results/notes
    failure = tc.find(namespace + "failure")
    error = tc.find(namespace + "error")
    message = ""

    if failure is not None:
        message = f"Failure message:\n{failure.attrib.get('message', '')}\n\n{failure.text or ''}"

    elif error is not None:
        message = f"Error message:\n{error.attrib.get('message', '')}\n\n{error.text or ''}"

    # Build TCMS test case description
    case_data = {
        "product": PRODUCT_ID,
        "category": CATEGORY_ID,
        "priority": 59,
        "case_status": 17,
        "summary": name,
        "text": (f"Original test function: `{classname}`.\n\n" f"Auto-imported from JUnit XML.\n\n" f"{message}"),
    }

    created = tcms.TestCase.create(case_data)
    print("Created case:")
    pprint.pprint(created)
    created_cases.append(created)

    print(f"Created case: {created['id']} - {name}")

    # Optional attach to plan
    if TESTPLAN_ID:
        tcms.TestPlan.add_case(TESTPLAN_ID, created["id"])


print(f"\nSuccessfully uploaded {len(created_cases)} cases.")
