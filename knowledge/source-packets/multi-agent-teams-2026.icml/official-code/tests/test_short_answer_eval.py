"""Tests for collaborative short-answer task evaluation logic."""

import unittest
from unittest.mock import MagicMock, patch

from teamwork.tasks.collaborative_short_answer_task import CollaborativeShortAnswerTask


# Create a minimal concrete implementation for testing (outside class so it's accessible in all tests)
class ConcreteShortAnswerTask(CollaborativeShortAnswerTask):
    def get_task_description(self, agent_id):
        return "test"
    def get_ground_truth(self):
        return "test"


class TestCollaborativeShortAnswerTaskEvaluation(unittest.TestCase):
    
    def setUp(self):
        self.task = ConcreteShortAnswerTask(agent_ids=[0], max_rounds=1, seed=0, use_llm_fallback=False)

    def test_extract_answer_basic(self):
        """Test basic extraction of 'My answer is X' format."""
        # Simple case
        self.assertEqual(self.task._extract_answer("My answer is December 6, 2016"), "December 6, 2016")
        
        # With period
        self.assertEqual(self.task._extract_answer("My answer is December 6, 2016."), "December 6, 2016")
        
        # With colon
        self.assertEqual(self.task._extract_answer("My answer is: December 6, 2016"), "December 6, 2016")
        
        # Case insensitive
        self.assertEqual(self.task._extract_answer("my answer is December 6, 2016"), "December 6, 2016")
        self.assertEqual(self.task._extract_answer("MY ANSWER IS December 6, 2016"), "December 6, 2016")

    def test_extract_answer_with_newline(self):
        """Test extraction when answer is on its own line (as instructed)."""
        # Answer on new line
        self.assertEqual(
            self.task._extract_answer("Reasoning here.\nMy answer is December 6, 2016"),
            "December 6, 2016"
        )
        
        # Answer on new line with period
        self.assertEqual(
            self.task._extract_answer("Reasoning here.\nMy answer is December 6, 2016."),
            "December 6, 2016"
        )
        
        # Answer on new line followed by more text
        self.assertEqual(
            self.task._extract_answer("Reasoning.\nMy answer is 42.\nMore text here."),
            "42"
        )


    def test_extract_answer_with_abbreviations(self):
        """Test extraction with abbreviations (on their own line)."""
        # Abbreviation with period on new line
        self.assertEqual(self.task._extract_answer("Reasoning.\nMy answer is Dr. Smith"), "Dr. Smith")
        
        # Multiple periods in abbreviation (trailing period removed, GPT-5 handles equivalence)
        self.assertEqual(self.task._extract_answer("My answer is U.S.A."), "U.S.A")
        
        # All caps abbreviation (trailing period removed)
        self.assertEqual(self.task._extract_answer("My answer is NASA."), "NASA")

    def test_extract_answer_with_commas(self):
        """Test extraction handles commas in answers."""
        # Date with comma
        self.assertEqual(self.task._extract_answer("My answer is December 6, 2016"), "December 6, 2016")
        
        # List with commas
        self.assertEqual(self.task._extract_answer("My answer is red, blue, green"), "red, blue, green")
        
        # Name with comma
        self.assertEqual(self.task._extract_answer("My answer is Smith, John"), "Smith, John")

    def test_extract_answer_fallback_patterns(self):
        """Test fallback to 'answer is X' without 'my'."""
        # Without "my"
        self.assertEqual(self.task._extract_answer("Answer is December 6, 2016"), "December 6, 2016")
        
        # With colon
        self.assertEqual(self.task._extract_answer("Answer is: 42"), "42")
        
        # Case insensitive
        self.assertEqual(self.task._extract_answer("ANSWER IS 42"), "42")

    def test_extract_answer_edge_cases(self):
        """Test edge cases and empty results."""
        # No pattern found
        self.assertEqual(self.task._extract_answer("Just some text without answer format"), "")
        
        # Empty string
        self.assertEqual(self.task._extract_answer(""), "")
        
        # Only "My answer is" with nothing after
        self.assertEqual(self.task._extract_answer("My answer is"), "")
        
        # Whitespace only
        self.assertEqual(self.task._extract_answer("My answer is   "), "")

    def test_extract_answer_numeric_answers(self):
        """Test extraction of numeric answers."""
        # Integer
        self.assertEqual(self.task._extract_answer("My answer is 42"), "42")
        
        # Float
        self.assertEqual(self.task._extract_answer("My answer is 3.14"), "3.14")
        
        # Negative number
        self.assertEqual(self.task._extract_answer("My answer is -5"), "-5")
        
        # Number with period at end
        self.assertEqual(self.task._extract_answer("My answer is 42."), "42")

    def test_extract_answer_with_trailing_punctuation(self):
        """Test handling of trailing punctuation."""
        # Semicolon
        self.assertEqual(self.task._extract_answer("My answer is 42;"), "42")
        
        # Colon
        self.assertEqual(self.task._extract_answer("My answer is 42:"), "42")
        
        # Multiple punctuation
        self.assertEqual(self.task._extract_answer("My answer is 42.;"), "42")

    def test_extract_answer_complex_cases(self):
        """Test complex real-world cases."""
        # Answer with parentheses
        self.assertEqual(self.task._extract_answer("My answer is (3, 4)"), "(3, 4)")
        
        # Answer with special characters
        self.assertEqual(self.task._extract_answer("My answer is $100"), "$100")
        
        # Answer with units
        self.assertEqual(self.task._extract_answer("My answer is 10 meters"), "10 meters")
        
        # Answer on new line (as instructed)
        self.assertEqual(
            self.task._extract_answer("After careful analysis.\nMy answer is December 6, 2016"),
            "December 6, 2016"
        )

    def test_is_equiv_always_uses_llm(self):
        """Test _is_equiv behavior with/without LLM fallback available."""
        # Exact matches should be treated as equivalent even without LLM fallback.
        self.assertTrue(self.task._is_equiv("December 6, 2016", "December 6, 2016"))

        # Non-exact matches should return False when LLM fallback is unavailable.
        self.assertFalse(self.task._is_equiv("Dec 6, 2016", "December 6, 2016"))

        # With LLM fallback enabled but no API key, exact match should still be True.
        task_with_llm = ConcreteShortAnswerTask(
            agent_ids=[0], max_rounds=1, seed=0, use_llm_fallback=True, llm_fallback_api_key=None
        )
        self.assertTrue(task_with_llm._is_equiv("December 6, 2016", "December 6, 2016"))

    @patch('teamwork.tasks.collaborative_short_answer_task.openai')
    def test_check_equiv_with_llm_yes_response(self, mock_openai):
        """Test LLM autorating with 'yes' response."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Both answers are the same date.\nyes"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        task = ConcreteShortAnswerTask(
            agent_ids=[0],
            max_rounds=1,
            seed=0,
            use_llm_fallback=True,
            llm_fallback_api_key="test-key"
        )
        
        result = task._check_equiv_with_llm("December 6, 2016", "December 6, 2016")
        self.assertTrue(result)

    @patch('teamwork.tasks.collaborative_short_answer_task.openai')
    def test_check_equiv_with_llm_no_response(self, mock_openai):
        """Test LLM autorating with 'no' response."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "These are different dates.\nno"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        task = ConcreteShortAnswerTask(
            agent_ids=[0],
            max_rounds=1,
            seed=0,
            use_llm_fallback=True,
            llm_fallback_api_key="test-key"
        )
        
        result = task._check_equiv_with_llm("December 6, 2016", "July 12, 2016")
        self.assertFalse(result)

    @patch('teamwork.tasks.collaborative_short_answer_task.openai')
    def test_check_equiv_with_llm_my_answer_is_yes(self, mock_openai):
        """Test LLM autorating when response is 'My answer is yes'."""
        # Mock OpenAI response with "My answer is yes" format
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Both answers are the same.\nMy answer is yes"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client
        
        task = ConcreteShortAnswerTask(
            agent_ids=[0],
            max_rounds=1,
            seed=0,
            use_llm_fallback=True,
            llm_fallback_api_key="test-key"
        )
        
        result = task._check_equiv_with_llm("December 6, 2016", "December 6, 2016")
        # Should extract "yes" from "My answer is yes" and return True
        self.assertTrue(result)

    def test_score_solution(self):
        """Test solution scoring."""
        # Incorrect answer should score 0.0.
        self.assertEqual(self.task.score_solution("My answer is December 6, 2016"), 0.0)

        # Correct answer should score 1.0 (ground truth is "test" in this concrete task).
        self.assertEqual(self.task.score_solution("My answer is test"), 1.0)
        
        # Empty answer should return 0.0
        self.assertEqual(self.task.score_solution("No answer format"), 0.0)


if __name__ == "__main__":
    unittest.main()

