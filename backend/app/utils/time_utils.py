from datetime import datetime
from zoneinfo import ZoneInfo
from app.core.config import settings

def now_local() -> datetime:
    """Return local time using configured timezone (naive datetime)."""
    tz_name = getattr(settings, 'TIMEZONE', None)
    if tz_name:
        try:
            tz = ZoneInfo(tz_name)
            return datetime.now(tz).replace(tzinfo=None)
        except Exception:
            pass
    # Fallback to system local timezone
    return datetime.now().astimezone().replace(tzinfo=None)
