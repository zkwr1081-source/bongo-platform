class VerificationResult:
    def __init__(self, ok, reason=""):
        self.ok = bool(ok)
        self.reason = reason

    def as_dict(self):
        return {
            "ok": self.ok,
            "reason": self.reason
        }

class Verifier:
    def verify(self, result):
        if result is None:
            return VerificationResult(False, "empty result")

        if isinstance(result, dict):
            if result.get("status") == "error":
                return VerificationResult(False, "result reports error")

        return VerificationResult(True, "accepted")
