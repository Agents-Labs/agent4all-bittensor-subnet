# Disable OpenTelemetry SDK
import os
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["EC_TELEMETRY"] = "false"
from .cli import Agent4ALL
from .version import __version__