from bongo.core.registry import Service

def ping(**kwargs):
    return {"ok": True, "message": "BONGO service is alive", "input": kwargs}

def echo(text="", **kwargs):
    return {"ok": True, "text": text}

def system_info(**kwargs):
    return {"ok": True, "service": "system-info"}

BUILTIN_SERVICES = [
    Service("system.ping", "system", ping, "BONGO health ping"),
    Service("utility.echo", "utility", echo, "Echo input"),
    Service("system.info", "system", system_info, "Basic system service"),
]
