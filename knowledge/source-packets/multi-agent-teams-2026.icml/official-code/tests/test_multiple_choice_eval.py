"""Tests for multiple choice task evaluation logic."""

from teamwork.tasks.collaborative_multiple_choice_task import CollaborativeMultipleChoiceQuestionTask
from teamwork.tasks.mmlu_pro_problem_task import MMLUProProblemTask
from teamwork.agent import TeamAgent
from teamwork.backends import EchoBackend
from teamwork.profiles import AgentProfile


class DummyMultipleChoiceTask(CollaborativeMultipleChoiceQuestionTask):
    """Test implementation of multiple choice task."""
    
    def __init__(self, question: str, options: list, answer: str, **kwargs):
        super().__init__(**kwargs)
        self.question = question
        self.options = options
        self.answer = answer
    
    def get_task_description(self, agent_id: int) -> str:
        option_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        options_text = "\n".join(
            f"{option_letters[i]}. {opt}" 
            for i, opt in enumerate(self.options[:len(option_letters)])
        )
        return f"{self.question}\n\n{options_text}"
    
    def get_ground_truth(self) -> str:
        return self.answer


def test_normalize_answer():
    """Test answer normalization for various formats."""
    task = DummyMultipleChoiceTask(
        question="Test",
        options=["A", "B", "C"],
        answer="A",
        agent_ids=[0],
        max_rounds=1,
        seed=42
    )
    
    # Test various formats
    assert task._normalize_answer("A") == "A"
    assert task._normalize_answer("(A)") == "A"
    assert task._normalize_answer("A)") == "A"
    assert task._normalize_answer("A.") == "A"
    assert task._normalize_answer("Answer: A") == "A"
    assert task._normalize_answer("The answer is A") == "A"
    assert task._normalize_answer("answer is A") == "A"
    assert task._normalize_answer("A ") == "A"
    assert task._normalize_answer("(B)") == "B"
    assert task._normalize_answer("C)") == "C"
    assert task._normalize_answer("D.") == "D"
    
    # Test case insensitivity
    assert task._normalize_answer("a") == "A"
    assert task._normalize_answer("(b)") == "B"
    
    # Test edge cases
    assert task._normalize_answer("") == ""
    assert task._normalize_answer("Not an answer") == ""


def test_extract_answer():
    """Test answer extraction from text."""
    task = DummyMultipleChoiceTask(
        question="Test",
        options=["A", "B", "C"],
        answer="A",
        agent_ids=[0],
        max_rounds=1,
        seed=42
    )
    
    # Test various formats
    assert task._extract_answer("The answer is A") == "A"
    assert task._extract_answer("I choose option B") == "B"
    assert task._extract_answer("Answer: C") == "C"
    assert task._extract_answer("(A)") == "A"
    assert task._extract_answer("A)") == "A"
    assert task._extract_answer("A.") == "A"
    assert task._extract_answer("After careful consideration, the answer is D.") == "D"
    assert task._extract_answer("My reasoning leads me to choose (E)") == "E"
    
    # Test with multiple mentions (should get last one)
    assert task._extract_answer("I think it's A, but actually B") == "B"
    
    # Test case insensitivity
    assert task._extract_answer("the answer is a") == "A"
    assert task._extract_answer("(b)") == "B"
    
    # Test exact format (priority pattern)
    assert task._extract_answer("The answer is 'A'") == "A"
    assert task._extract_answer("The answer is 'I'") == "I"
    assert task._extract_answer("The answer is 'B'.") == "B"
    
    # Test "I" pronoun handling - should NOT match pronoun "I"
    assert task._extract_answer("I agree with the team") == ""
    assert task._extract_answer("I think the answer is B") == "B"  # Should extract B, not I
    assert task._extract_answer("I believe we should choose C") == "C"  # Should extract C, not I
    
    # Test "I" as actual answer choice - should match when clearly in answer context
    assert task._extract_answer("The answer is 'I'") == "I"
    assert task._extract_answer("After discussion, the answer is I") == "I"
    assert task._extract_answer("Option I is correct") == "I"


def test_is_equiv_strict_match():
    """Test strict matching for equivalent answers."""
    task = DummyMultipleChoiceTask(
        question="Test",
        options=["A", "B", "C"],
        answer="A",
        agent_ids=[0],
        max_rounds=1,
        seed=42,
        use_llm_fallback=False  # Disable LLM for these tests
    )
    
    # Exact matches
    assert task._is_equiv("A", "A") is True
    assert task._is_equiv("B", "B") is True
    
    # Case insensitive
    assert task._is_equiv("a", "A") is True
    assert task._is_equiv("A", "a") is True
    assert task._is_equiv("b", "B") is True
    
    # Different formats that normalize to same letter
    assert task._is_equiv("(A)", "A") is True
    assert task._is_equiv("A)", "A") is True
    assert task._is_equiv("A.", "A") is True
    assert task._is_equiv("Answer: A", "A") is True
    assert task._is_equiv("The answer is A", "A") is True
    
    # Non-matches
    assert task._is_equiv("A", "B") is False
    assert task._is_equiv("B", "C") is False
    assert task._is_equiv("(A)", "B") is False


def test_is_equiv_with_llm_fallback():
    """Test that LLM fallback is used when strict match fails."""
    task = DummyMultipleChoiceTask(
        question="Test",
        options=["A", "B", "C"],
        answer="A",
        agent_ids=[0],
        max_rounds=1,
        seed=42,
        use_llm_fallback=False  # Disable for unit tests (would require API key)
    )
    
    # Without LLM fallback, should return False for non-matches
    assert task._is_equiv("A", "B") is False
    
    # Note: Full LLM fallback testing would require API key and actual API calls


def test_mmlu_pro_task_initialization():
    """Test MMLU Pro task initialization."""
    problem_data = {
        'question_id': 'test_001',
        'question': 'What is 2+2?',
        'options': ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
        'answer': 'C'  # Option C is the 3rd option (index 2)
    }
    
    task = MMLUProProblemTask(
        agent_ids=[0, 1],
        max_rounds=2,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42
    )
    
    assert task.question_id == 'test_001'
    assert task.question_text == 'What is 2+2?'
    assert len(task.options) == 10
    assert task.answer == 'C'


def test_mmlu_pro_task_description():
    """Test MMLU Pro task description formatting."""
    problem_data = {
        'question_id': 'test_001',
        'question': 'What is 2+2?',
        'options': ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
        'answer': 'C'
    }
    
    task = MMLUProProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42
    )
    
    description = task.get_task_description(0)
    assert 'What is 2+2?' in description
    assert 'A. 2' in description
    assert 'B. 3' in description
    assert 'C. 4' in description
    assert 'J. 11' in description


def test_mmlu_pro_ground_truth_letter():
    """Test ground truth extraction when answer is a letter."""
    problem_data = {
        'question_id': 'test_001',
        'question': 'Test',
        'options': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
        'answer': 'D'
    }
    
    task = MMLUProProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42
    )
    
    assert task.get_ground_truth() == 'D'


def test_mmlu_pro_ground_truth_index():
    """Test ground truth extraction when answer is an index."""
    problem_data = {
        'question_id': 'test_001',
        'question': 'Test',
        'options': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'],
        'answer': '3'  # Index 3 = option D
    }
    
    task = MMLUProProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42
    )
    
    assert task.get_ground_truth() == 'D'


def test_mmlu_pro_task_execution():
    """Test basic task execution with echo backend."""
    problem_data = {
        'question_id': 'test_001',
        'question': 'What is 2+2?',
        'options': ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
        'answer': 'C'  # Option C (index 2) = '4'
    }
    
    task = MMLUProProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42,
        use_llm_fallback=False
    )
    
    backend = EchoBackend()
    agent = TeamAgent(
        profile=AgentProfile(
            agent_id=0,
            name="TestAgent",
            role="Expert",
            system_prompt="You are a helpful expert."
        ),
        backend=backend
    )
    
    result = task.execute([agent])
    
    assert result.score in [0.0, 1.0]  # Should be binary (correct/incorrect)
    assert "ground_truth" in result.metadata
    assert "individual_answers" in result.metadata
    assert "team_answer" in result.metadata
    assert result.metadata["ground_truth"] == "C"

