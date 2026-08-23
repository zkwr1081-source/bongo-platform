import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bongo import create_runtime

runtime = create_runtime(1000)

services = runtime.registry.list()
capabilities = sum(
    len(runtime.integration.capabilities.get(s.name))
    for s in services
)

print("==========================================")
print(" بونجو — ممر الحلول المتكامل")
print("==========================================")
print("STATUS:", runtime.status()["status"])
print("SERVICES:", len(services))
print("CAPABILITIES:", capabilities)
print("CATEGORIES:", len(runtime.registry.categories()))

results = runtime.integration.find("translation")

print("DISCOVERY RESULTS:", len(results))

if results:
    print("DISCOVERY SAMPLE:", results[0])

result = runtime.integration.execute(
    "ai.service_0001",
    source="بونجو"
)

print("EXECUTION:", result)
print("==========================================")
