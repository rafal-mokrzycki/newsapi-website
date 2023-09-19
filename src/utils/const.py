import re

# Date in ISO-8601 format
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATE_LEN = len("YYYY-MM-DD")
DATE_FMT = "%Y-%m-%d"

# Datetime in ISO-8601 format
DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
DATETIME_LEN = len("YYYY-MM-DDTHH:MM:SS")
DATETIME_FMT = "%Y-%m-%dT%H:%M:%S"

# Google Cloud Storage naming convention
MAX_LENGTH = 63
MIN_LENGTH = 3
