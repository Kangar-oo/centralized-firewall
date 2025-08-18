# log_service.py

from models.db import db, Log

def add_log(event, details, timestamp):
    log_entry = Log(event=event, details=details, timestamp=timestamp)
    db.session.add(log_entry)
    db.session.commit()
    return log_entry

def get_all_logs():
    logs = Log.query.all()
    result = [{"event": l.event, "details": l.details, "time": l.timestamp} for l in logs]
    return result
