from bongo import create_runtime

runtime = create_runtime()

print("================================")
print(" BONGO — ممر الحلول المتكامل")
print("================================")
print("Status:", runtime.status())
print("Services:", runtime.registry.count())
print("Categories:", ", ".join(runtime.registry.categories()))
print("Ping:", runtime.router.dispatch("system.ping"))
