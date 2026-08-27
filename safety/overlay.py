"""Safety overlay — the part that keeps the autonomous forklift from murdering someone.

Rules engine + kill switch. Human-in-the-loop gates for the 20% that needs a brain.
"""

from datetime import datetime


class SafetyOverlay:
    def __init__(self):
        self.kill_switch_active = False
        self.rules = []

    def add_rule(self, condition, action, severity="warning"):
        self.rules.append({"condition": condition, "action": action, "severity": severity})

    def evaluate(self, asset) -> list[dict]:
        """Run all rules against an asset. Returns triggered actions."""
        if self.kill_switch_active:
            return [{"action": "EMERGENCY_STOP", "severity": "critical", "reason": "kill switch"}]
        triggered = []
        for rule in self.rules:
            if rule["condition"](asset):
                triggered.append({"action": rule["action"], "severity": rule["severity"], "ts": datetime.utcnow().isoformat()})
        return triggered

    def trigger_kill_switch(self, reason: str):
        self.kill_switch_active = True
        return f"KILL SWITCH: {reason}"


# Example rules — expand as we go
def restricted_zone_breach(asset):
    return asset.properties.get("in_restricted_zone", False)


def cert_expired(asset):
    return asset.properties.get("cert_expiry") and asset.properties["cert_expiry"] < datetime.utcnow()
