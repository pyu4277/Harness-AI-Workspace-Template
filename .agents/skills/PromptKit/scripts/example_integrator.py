class ExampleIntegrator:
    """
    Hook controller for ExampleChatGenerator.
    Injects few-shot examples into the prompt planning phase to visualize outcomes.
    """
    def __init__(self, prompt_plan):
        self.prompt_plan = prompt_plan
        self.examples = []

    def generate_examples(self, num_examples=3):
        """
        기획된 프롬프트 파트(Hybrid 조합)를 바탕으로,
        실제 결과물이 어떤 형태일지 직관적인 예시를 생성합니다.
        (실제 서비스에서는 LLM을 통해 컨텍스트에 맞는 예시를 자동 산출합니다.)
        """
        # TODO: Call ExampleChatGenerator mechanism or LLM API to generate examples
        print(f"[ExampleIntegrator] 분석된 기획안 기반으로 {num_examples}개의 예시를 생성 중...")
        
        # Scaffolding mock data
        self.examples = [
            "- 예시 1: 입력 [A, B, C] -> 출력 {json formatting...}",
            "- 예시 2: 입력 [모호한 조건] -> 에러 반환 및 재질의 유도",
            "- 예시 3: 입력 [극단적 엣지 케이스] -> 안전 통제망 발동",
        ]
        
        return self.examples

if __name__ == "__main__":
    integrator = ExampleIntegrator("CoT와 Role-Prompting 조합 기획안")
    res = integrator.generate_examples()
    for r in res:
        print(r)
