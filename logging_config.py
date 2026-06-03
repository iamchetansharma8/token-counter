import logging

import structlog

# 1. Define standard library logging handler for the file and console
file_handler = logging.FileHandler("Files/production.log")
console_handler = logging.StreamHandler()
file_handler.setLevel(logging.INFO)

# 2. Configure root logger
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

def setup_logging(level="INFO"):
    """Configure JSON logging for the tool."""
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True
    )

log = structlog.get_logger()
