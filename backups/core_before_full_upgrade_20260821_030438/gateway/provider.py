class ProviderResult:
    def __init__(self, provider, model, answer):
        self.provider = provider
        self.model = model
        self.answer = answer

    def as_dict(self):
        return {
            "provider": self.provider,
            "model": self.model,
            "answer": self.answer,
        }
