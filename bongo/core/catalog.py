from bongo.core.registry import Service

CATEGORIES = [
    "ai", "search", "data", "files", "text",
    "translation", "developer", "business", "education",
    "media", "system", "utility", "automation", "security",
    "memory", "analytics", "productivity", "integration",
    "communication", "knowledge"
]

def generic_handler(service_name, category, **kwargs):
    return {
        "ok": True,
        "service": service_name,
        "category": category,
        "message": f"{service_name} executed successfully",
        "input": kwargs
    }

def generate_services(count=1000):
    services = []

    for i in range(1, count + 1):
        category = CATEGORIES[(i - 1) % len(CATEGORIES)]
        name = f"{category}.service_{i:04d}"

        def handler(_name=name, _category=category, **kwargs):
            return generic_handler(_name, _category, **kwargs)

        services.append(
            Service(
                name=name,
                category=category,
                handler=handler,
                description=f"بونجو integrated service {name}",
                metadata={
                    "id": i,
                    "generated": True,
                    "version": "1.0"
                }
            )
        )

    return services
