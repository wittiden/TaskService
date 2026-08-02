import logging

import sentry_sdk
from sentry_sdk.integrations.loguru import LoguruIntegration

from app.common.config import application_config
from app.common.observability.events.config import event_config


def setup_sentry() -> None:
    if application_config.is_test:
        return

    sentry_sdk.init(
        dsn=event_config.SENTRY_DSN,
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        # Enable sending logs to Sentry
        enable_logs=True,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=0.1,
        integrations=[
            LoguruIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
                sentry_logs_level=logging.INFO,
            )
        ],
    )
