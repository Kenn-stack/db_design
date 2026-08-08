from datetime import datetime, timedelta
import random

# Define a starting base date (e.g., 30 days ago)
START_DATE = datetime.now() - timedelta(days=30)


def generate_steady_timestamp(n):
  """Generates a timestamp that steadily advances over time.

  `n` is the sequence number (0, 1, 2, ...).
  """
  base_offset = timedelta(hours=4 * n)

  jitter = timedelta(minutes=random.randint(-30, 30))

  return START_DATE + base_offset + jitter