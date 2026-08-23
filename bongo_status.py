from bongo import create_runtime

runtime = create_runtime(1000)

print("==========================================")
print(" بونجو — ممر الحلول المتكامل")
print("==========================================")
print("STATUS:", runtime.status()["status"])
print("TOTAL SERVICES:", runtime.registry.count())
print("CATEGORIES:", len(runtime.registry.categories()))
print("FIRST:", runtime.registry.list()[3].name)
print("LAST:", runtime.registry.list()[-1].name)
print("TEST SERVICE:", runtime.router.dispatch("ai.service_0001", source="status"))
print("==========================================")
