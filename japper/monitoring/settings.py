import datetime

from django.conf import settings


# Minimum number of identical consecutive check result statuses needed to
# change the status of a state
MIN_CONSECUTIVE_STATUSES = getattr(settings,
        'JAPPER_MONITORING_MIN_CONSECUTIVE_STATUSES', 3)

# States coming from dynamic hosts monitoring sources that have not been
# updated for more than this period are automatically cleaned up
STATES_TTL = datetime.timedelta(hours=1)
