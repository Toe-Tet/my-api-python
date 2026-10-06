import logging
import sys
import traceback

import structlog


def format_exc_info_as_list(
    logger,
    method_name,
    event_dict,
):
    exc_info = event_dict.pop("exc_info", None)

    if exc_info:
        if exc_info is True:
            exc_info = sys.exc_info()

        event_dict["exception"] = traceback.format_exception(*exc_info)

    return event_dict


def setup_logging() -> None:
    timestamper = structlog.processors.TimeStamper(
        fmt="iso",
    )

    # Processors applied to standard logging records
    pre_chain = [
        structlog.contextvars.merge_contextvars,
        timestamper,
        structlog.stdlib.add_log_level,
    ]

    # JSON formatter
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=pre_chain,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    # Configure standard Python logging
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[handler],
        force=True,
    )

    # Configure Structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            timestamper,
            structlog.processors.StackInfoRenderer(),
            # Convert exception information into
            # an array of traceback lines.
            format_exc_info_as_list,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
