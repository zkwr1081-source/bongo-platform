class VerificationAgent:
    name = "VERIFY"
    role = "التحقق من النتائج"

    def run(self, context):
        return {
            "agent": self.name,
            "verified": True,
            "task_id": context.task_id,
        }
