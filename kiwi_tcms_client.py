import os

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

# 1. Create a test case
tc = client.exec.TestCase.create(
    {
        "product": 61,
        "category": 135,
        "summary": "My new UAT test case",
        "priority": 1,
        # other fields...
    }
)

case_id = tc["id"]

# 2. (Optionally) find or create a TestPlan, but assume plan_id = 123

# 3. Create a TestRun
tr = client.exec.TestRun.create(
    {
        "plan_id": 123,
        "build": "v1.2.3",
        "summary": "UAT Run for build v1.2.3",
        "manager_id": 17,
        "default_tester_id": 17,
    }
)

run_id = tr["id"]

# 4. Add test case to run
client.exec.TestRun.add_case(run_id, case_id)

# 5. After test execution, update result (assuming appropriate method: e.g. TestExecution.update)...
# (This part depends on which RPC endpoint your TCMS exposes for execution results.)
