class RuleBasedLLMClient:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        return f"{system_prompt.strip()} :: {user_prompt.strip()}"
