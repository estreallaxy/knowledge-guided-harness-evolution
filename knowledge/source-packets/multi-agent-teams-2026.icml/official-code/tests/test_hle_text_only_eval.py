"""Tests for HLE Text-Only task evaluation logic."""

from unittest.mock import patch

from teamwork.tasks.hle_text_only_problem_task import HLETextOnlyProblemTask


def test_hle_task_initialization():
    """Test HLETextOnlyProblemTask initialization."""
    problem_data = {
        'question': 'What is 2+2?\nA. 3\nB. 4\nC. 5',
        'answer': 'B',
        'id': 'test_001'
    }
    
    task = HLETextOnlyProblemTask(
        agent_ids=[0, 1],
        max_rounds=2,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42
    )
    
    assert task.question_text == problem_data['question']
    assert task.answer == problem_data['answer']
    assert task.unique_id == 'test_001'
    assert task.name == 'HLETextOnly-test_001'


def test_hle_get_task_description():
    """Test get_task_description returns question text with instructions."""
    problem_data = {
        'question': 'What is 2+2?\nA. 3\nB. 4\nC. 5',
        'answer': 'B',
        'id': 'test_001'
    }
    
    task = HLETextOnlyProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42
    )
    
    description = task.get_task_description(agent_id=0)
    assert 'What is 2+2?' in description
    assert 'A. 3' in description
    assert 'B. 4' in description
    assert 'C. 5' in description
    assert 'explain your reasoning' in description.lower()
    assert 'output your answer on a new line' in description.lower()


def test_hle_get_ground_truth():
    """Test get_ground_truth returns normalized answer letter."""
    problem_data = {
        'question': 'Test question',
        'answer': 'B',
        'id': 'test_001'
    }
    
    task = HLETextOnlyProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42
    )
    
    assert task.get_ground_truth() == 'B'
    
    # Test with lowercase
    problem_data['answer'] = 'c'
    task2 = HLETextOnlyProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_002',
        seed=42
    )
    assert task2.get_ground_truth() == 'C'
    
    # Test with whitespace
    problem_data['answer'] = ' D '
    task3 = HLETextOnlyProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_003',
        seed=42
    )
    assert task3.get_ground_truth() == 'D'


def test_hle_answer_normalization():
    """Test answer normalization with various formats."""
    problem_data = {
        'question': 'Test',
        'answer': 'A',
        'id': 'test_001'
    }
    
    task = HLETextOnlyProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
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
    
    # Test case insensitivity
    assert task._normalize_answer("a") == "A"
    assert task._normalize_answer("(b)") == "B"


def test_hle_answer_extraction():
    """Test answer extraction from agent responses."""
    problem_data = {
        'question': 'Test',
        'answer': 'A',
        'id': 'test_001'
    }
    
    task = HLETextOnlyProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42
    )
    
    # Test various formats
    assert task._extract_answer("The answer is A") == "A"
    assert task._extract_answer("I choose option B") == "B"
    assert task._extract_answer("Answer: C") == "C"
    assert task._extract_answer("(A)") == "A"
    assert task._extract_answer("A)") == "A"
    assert task._extract_answer("A.") == "A"
    
    # Test with reasoning followed by answer on new line
    assert task._extract_answer("After careful consideration\nB") == "B"
    assert task._extract_answer("My reasoning:\nThe answer is C") == "C"


def test_hle_equivalence_exact_match():
    """Test equivalence checking with exact match."""
    problem_data = {
        'question': 'Test question',
        'answer': 'B',
        'id': 'test_001'
    }
    
    task = HLETextOnlyProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42,
        use_llm_fallback=False
    )
    
    # Exact match should return True
    assert task._is_equiv("B", "B")
    assert task._is_equiv("b", "B")  # Case insensitive
    assert task._is_equiv("(B)", "B")  # Normalization
    assert task._is_equiv("B)", "B")
    
    # Non-match should return False
    assert not task._is_equiv("A", "B")
    assert not task._is_equiv("C", "B")


def test_hle_equivalence_substring_then_llm():
    """Test equivalence checking: exact match fails, then substring check, then LLM fallback."""
    problem_data = {
        'question': 'Test question',
        'answer': 'B',
        'id': 'test_001'
    }
    
    task = HLETextOnlyProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42,
        use_llm_fallback=True,
        llm_fallback_api_key="test_key"
    )
    
    # Test case where gold is substring of predicted (should trigger LLM fallback)
    # Use a case where normalization doesn't make them exact match
    # For example: predicted has extra text that doesn't normalize to just the letter
    # But the normalized gold "B" is still a substring of the normalized predicted
    with patch.object(task, '_check_equiv_with_llm', return_value=True) as mock_llm:
        # If predicted normalizes to something like "BEXTRA" and gold is "B"
        # This is a contrived case, but tests the substring logic
        # Actually, let's use a real case: model says "B)" and gold is "B"
        # After normalization: predicted="B", gold="B" -> exact match, so that won't work
        # Let's test with a case where we manually set up the scenario
        # We'll patch _normalize_answer to return different values for testing
        with patch.object(task, '_normalize_answer', side_effect=lambda x: "BEXTRA" if x == "BEXTRA" else "B"):
            # Predicted normalizes to "BEXTRA", gold normalizes to "B"
            # Exact match fails, but "B" is substring of "BEXTRA", so should call LLM
            result = task._is_equiv("BEXTRA", "B")
            assert result
            mock_llm.assert_called_once()
    
    # Test case where gold is NOT substring of predicted (should NOT trigger LLM)
    with patch.object(task, '_check_equiv_with_llm', return_value=False) as mock_llm:
        # Gold "B" is not substring of predicted "A" (after normalization)
        result = task._is_equiv("A", "B")
        assert not result
        # Should not call LLM fallback
        mock_llm.assert_not_called()
    
    # Test case where exact match succeeds (should NOT trigger LLM)
    with patch.object(task, '_check_equiv_with_llm', return_value=False) as mock_llm:
        result = task._is_equiv("B", "B")
        assert result
        # Should not call LLM fallback since exact match succeeded
        mock_llm.assert_not_called()


def test_hle_equivalence_no_llm_fallback():
    """Test equivalence checking without LLM fallback."""
    problem_data = {
        'question': 'Test question',
        'answer': 'B',
        'id': 'test_001'
    }
    
    task = HLETextOnlyProblemTask(
        agent_ids=[0],
        max_rounds=1,
        problem_data=problem_data,
        unique_id='test_001',
        seed=42,
        use_llm_fallback=False
    )
    
    # Exact match should work
    assert task._is_equiv("B", "B")
    
    # "Answer: B" normalizes to "B", so exact match succeeds (no LLM needed)
    assert task._is_equiv("Answer: B", "B")
    
    # Test case where exact match fails and substring check would pass, but LLM is disabled
    # Use a case where normalization doesn't make them match
    with patch.object(task, '_normalize_answer', side_effect=lambda x: "BEXTRA" if x == "BEXTRA" else "B"):
        # Predicted normalizes to "BEXTRA", gold normalizes to "B"
        # Exact match fails, substring check would pass, but LLM is disabled
        # Should return False
        result = task._is_equiv("BEXTRA", "B")
        assert not result

