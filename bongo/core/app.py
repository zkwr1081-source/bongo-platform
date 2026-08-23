from bongo.core.runtime import BongoRuntime
from bongo.services.builtin import BUILTIN_SERVICES
from bongo.core.catalog import generate_services
from bongo.core.integration import IntegrationLayer

def create_runtime(service_count=1000):
    runtime = BongoRuntime()

    for service in BUILTIN_SERVICES:
        runtime.register(service)

    for service in generate_services(service_count):
        runtime.register(service)

    runtime.integration = IntegrationLayer(runtime)

    for service in runtime.registry.list():
        runtime.integration.register_service_capability(
            service.name,
            name=f"{service.name}.execute",
            description=service.description,
            tags=[service.category, "bongo", "service"],
            input_schema={"type": "object"},
            output_schema={"type": "object"}
        )

    return runtime
