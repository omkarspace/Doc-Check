import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Union

import pytz
from dateutil import parser

from app.config import settings
from app.logger import logger

def now_utc() -> datetime:
    """Get current UTC datetime with timezone awareness."""
    return datetime.now(timezone.utc)

def now_local() -> datetime:
    """Get current local datetime with timezone awareness."""
    return datetime.now(get_local_timezone())

def get_local_timezone() -> timezone:
    """Get the local timezone from settings or system."""
    if settings.TIMEZONE:
        try:
            return pytz.timezone(settings.TIMEZONE)
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone in settings: {settings.TIMEZONE}. Using system timezone.")
    
    # Fall back to system timezone
    return datetime.now().astimezone().tzinfo

def parse_datetime(
    dt_str: str, 
    timezone_str: str = None, 
    is_dst: bool = False
) -> datetime:
    """
    Parse a datetime string with timezone handling.
    
    Args:
        dt_str: Datetime string to parse
        timezone_str: Timezone string (e.g., 'UTC', 'America/New_York')
        is_dst: Whether to consider DST for ambiguous times
        
    Returns:
        Timezone-aware datetime object
    """
    try:
        dt = parser.parse(dt_str)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid datetime string: {dt_str}") from e
    
    # If the datetime is naive, localize it
    if dt.tzinfo is None:
        if timezone_str:
            tz = pytz.timezone(timezone_str)
        else:
            tz = get_local_timezone()
        
        # Handle ambiguous times (e.g., during DST transitions)
        if hasattr(tz, 'localize'):
            try:
                dt = tz.localize(dt, is_dst=is_dst)
            except Exception:
                # Fallback to naive conversion if localization fails
                dt = dt.replace(tzinfo=tz)
        else:
            dt = dt.replace(tzinfo=tz)
    
    return dt

def to_utc(dt: datetime) -> datetime:
    """Convert a datetime to UTC timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=get_local_timezone())
    return dt.astimezone(timezone.utc)

def to_local(dt: datetime) -> datetime:
    """Convert a datetime to local timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(get_local_timezone())

def format_datetime(
    dt: datetime, 
    format_str: str = None,
    timezone_str: str = None
) -> str:
    """
    Format a datetime object as a string.
    
    Args:
        dt: Datetime object to format
        format_str: Format string (default: ISO format)
        timezone_str: Timezone to convert to before formatting
    """
    if dt is None:
        return ""
    
    # Convert to specified timezone if provided
    if timezone_str:
        tz = pytz.timezone(timezone_str)
        dt = dt.astimezone(tz)
    
    # Format the datetime
    if format_str is None:
        return dt.isoformat()
    
    return dt.strftime(format_str)

def humanize_delta(
    dt: datetime,
    precision: str = 'seconds',
    add_suffix: bool = False
) -> str:
    """
    Convert a datetime to a human-readable relative time string.
    
    Args:
        dt: The datetime to convert
        precision: The smallest unit to display ('seconds', 'minutes', 'hours', 'days')
        add_suffix: Whether to add 'ago' or 'from now' suffix
    
    Returns:
        Human-readable time difference (e.g., '2 hours ago')
    """
    now = now_utc()
    delta = now - dt if now > dt else dt - now
    
    # Handle future dates
    is_future = dt > now
    
    # Calculate time differences
    seconds = int(delta.total_seconds())
    minutes = seconds // 60
    hours = minutes // 60
    days = delta.days
    months = days // 30
    years = days // 365
    
    # Determine the appropriate unit
    if years > 0:
        value = years
        unit = 'year'
    elif months > 0:
        value = months
        unit = 'month'
    elif days > 0:
        value = days
        unit = 'day'
    elif hours > 0 or precision == 'hours':
        value = hours
        unit = 'hour'
    elif minutes > 0 or precision == 'minutes':
        value = minutes
        unit = 'minute'
    else:
        value = seconds
        unit = 'second'
    
    # Pluralize
    if value != 1:
        unit += 's'
    
    result = f"{value} {unit}"
    
    # Add suffix if requested
    if add_suffix:
        if is_future:
            result += " from now"
        else:
            result += " ago"
    
    return result

def get_timestamp(unit: str = 'ms') -> Union[int, float]:
    """
    Get current timestamp in the specified unit.
    
    Args:
        unit: The unit of the timestamp ('ms' for milliseconds, 's' for seconds, 'ns' for nanoseconds)
    
    Returns:
        Timestamp as integer or float
    """
    t = time.time()
    
    if unit == 'ms':
        return int(t * 1000)
    elif unit == 's':
        return int(t)
    elif unit == 'ns':
        return int(t * 1e9)
    elif unit == 'float':
        return t
    else:
        raise ValueError(f"Unsupported timestamp unit: {unit}")

def parse_duration(duration_str: str) -> timedelta:
    """
    Parse a duration string into a timedelta.
    
    Supports formats like:
    - '1h30m' (1 hour and 30 minutes)
    - '2d' (2 days)
    - '1w' (1 week)
    - '1h' (1 hour)
    - '30m' (30 minutes)
    - '30s' (30 seconds)
    
    Args:
        duration_str: Duration string to parse
        
    Returns:
        timedelta representing the duration
    """
    if not duration_str:
        raise ValueError("Empty duration string")
    
    # Define units in seconds
    units = {
        'w': 604800,  # week
        'd': 86400,   # day
        'h': 3600,    # hour
        'm': 60,      # minute
        's': 1,       # second
    }
    
    seconds = 0
    num_str = ''
    
    for char in duration_str.lower():
        if char.isdigit() or char == '.':
            num_str += char
        elif char in units:
            if not num_str:
                raise ValueError(f"No number specified for unit '{char}'")
            try:
                num = float(num_str)
            except ValueError:
                raise ValueError(f"Invalid number: {num_str}")
            seconds += num * units[char]
            num_str = ''
        elif not char.isspace():
            raise ValueError(f"Invalid character in duration: {char}")
    
    if num_str:
        raise ValueError(f"Number without unit: {num_str}")
    
    return timedelta(seconds=seconds)
