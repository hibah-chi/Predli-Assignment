class CostTracker:
    """Track token usage and USD cost per model."""

    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
        self.events = []  # list of dicts: model, prompt_tokens, completion_tokens, cost
        self.total_characters = 0  # backward compatibility for legacy add()

    def add_usage(self, model: str, prompt_tokens: int, completion_tokens: int, cost_usd: float):
        self.total_input_tokens += prompt_tokens
        self.total_output_tokens += completion_tokens
        self.total_cost_usd += cost_usd
        self.events.append(
            {
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost_usd": cost_usd,
            }
        )

    def add(self, text: str):
        # legacy compatibility; track chars if needed elsewhere
        if text:
            self.total_characters += len(text)

    def estimate_tokens(self):
        return self.total_input_tokens + self.total_output_tokens

    def estimate_cost_usd(self):
        return self.total_cost_usd

    def summary(self):
        return {
            "prompt_tokens": self.total_input_tokens,
            "completion_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": self.total_cost_usd,
            "events": self.events,
        }
