# rule_service.py

# Simple in-memory rule storage (can later be DB)
rules = [
    {"type": "BLOCK", "target": "192.168.1.100"},
    {"type": "ALLOW", "target": "8.8.8.8"}
]

def get_rules():
    return rules

def add_rule(rule_type, target):
    rule = {"type": rule_type, "target": target}
    rules.append(rule)
    return rule

def check_rule(ip):
    """
    Check if an IP matches a rule.
    Returns 'BLOCKED', 'ALLOWED', or 'UNKNOWN'
    """
    for rule in rules:
        if rule["target"] == ip:
            if rule["type"] == "BLOCK":
                return "BLOCKED"
            elif rule["type"] == "ALLOW":
                return "ALLOWED"
    return "ALLOWED"  # Default allow if not blocked
