from datetime import datetime, timedelta

def daterange(start_date, end_date):
    """Gera datas de start_date até end_date (ambos inclusive)."""
    curr = start_date
    while curr <= end_date:
        yield curr
        curr += timedelta(days=1)
