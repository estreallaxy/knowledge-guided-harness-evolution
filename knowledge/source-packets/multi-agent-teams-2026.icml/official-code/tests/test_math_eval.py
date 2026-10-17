"""Tests for collaborative math task evaluation logic."""

import unittest

from teamwork.tasks.collaborative_math_task import CollaborativeMathTask


class TestCollaborativeMathTaskEvaluation(unittest.TestCase):
    
    def setUp(self):
        # Create a minimal concrete implementation for testing
        class ConcreteMathTask(CollaborativeMathTask):
            def get_task_description(self, agent_id):
                return "test"
            def get_ground_truth(self):
                return "test"
                
        self.task = ConcreteMathTask(agent_ids=[0], max_rounds=1, seed=0)

    def test_extract_answer_boxed(self):
        """Test extraction of \\boxed{...} content."""
        # Simple boxed
        self.assertEqual(self.task._extract_answer("The answer is \\boxed{42}"), "42")
        
        # Nested braces in boxed
        self.assertEqual(self.task._extract_answer("Result: \\boxed{\\frac{1}{2}}"), "\\frac{1}{2}")
        
        # Multiple boxed (should take last)
        self.assertEqual(
            self.task._extract_answer("First \\boxed{10}, but actually \\boxed{20}"), 
            "20"
        )
        
        # Boxed with text around
        self.assertEqual(
            self.task._extract_answer("Therefore, \\boxed{x=5} is correct."), 
            "x=5"
        )

    def test_extract_answer_fallback(self):
        """Test fallback extraction when no boxed content is present."""
        # Last line
        self.assertEqual(self.task._extract_answer("Calculation steps...\n42"), "42")
        
        # Single line
        self.assertEqual(self.task._extract_answer("100"), "100")
        
        # Text with number at end
        self.assertEqual(self.task._extract_answer("The answer is 5"), "5")
        self.assertEqual(self.task._extract_answer("The answer is 5."), "5")
        self.assertEqual(self.task._extract_answer("Answer: 1/2"), "1/2")
        self.assertEqual(self.task._extract_answer("x = 5"), "5")

    def test_is_equiv_exact(self):
        """Test exact string equivalence."""
        self.assertTrue(self.task._is_equiv("42", "42"))
        self.assertTrue(self.task._is_equiv("x+y", "x+y"))
        
        # Whitespace insensitive
        self.assertTrue(self.task._is_equiv(" 42 ", "42"))
        self.assertTrue(self.task._is_equiv("x + y", "x+y"))

    def test_is_equiv_latex_normalization(self):
        """Test LaTeX normalization."""
        # \dfrac vs \frac
        self.assertTrue(self.task._is_equiv("\\dfrac{1}{2}", "\\frac{1}{2}"))
        self.assertTrue(self.task._is_equiv("\\tfrac{1}{2}", "\\frac{1}{2}"))
        
        # Double backslash removal
        self.assertTrue(self.task._is_equiv("42\\\\", "42"))

    def test_is_equiv_numeric(self):
        """Test numeric equivalence."""
        # Integer vs Float
        self.assertTrue(self.task._is_equiv("42", "42.0"))
        self.assertTrue(self.task._is_equiv("1", "1.000"))
        
        # Small differences (within tolerance)
        self.assertTrue(self.task._is_equiv("0.3333333", "0.3333333"))

    def test_is_equiv_sympy(self):
        """Test SymPy-based equivalence."""
        # Fractions
        self.assertTrue(self.task._is_equiv("1/2", "0.5"))
        self.assertTrue(self.task._is_equiv("\\frac{1}{2}", "0.5"))
        
        # Simple algebra
        self.assertTrue(self.task._is_equiv("x + y", "y + x"))
        self.assertTrue(self.task._is_equiv("2*x", "x + x"))
        
        # Boxed wrapper handling in gold/pred
        self.assertTrue(self.task._is_equiv("\\boxed{42}", "42"))
        self.assertTrue(self.task._is_equiv("42", "\\boxed{42}"))
        
    def test_is_equiv_negatives(self):
        """Test cases that should NOT be equivalent."""
        self.assertFalse(self.task._is_equiv("42", "43"))
        self.assertFalse(self.task._is_equiv("x", "y"))
        self.assertFalse(self.task._is_equiv("1/2", "1/3"))

    def test_is_equiv_coordinates(self):
        """Test coordinate pair equivalence with different LaTeX formatting."""
        # The original problematic case: \left( 3, \frac{\pi}{2} \right) vs \boxed{(3, \pi/2)}
        self.assertTrue(
            self.task._is_equiv(
                r"\left( 3, \frac{\pi}{2} \right)",
                r"\boxed{(3, \pi/2)}"
            )
        )
        
        # Reverse order
        self.assertTrue(
            self.task._is_equiv(
                r"\boxed{(3, \pi/2)}",
                r"\left( 3, \frac{\pi}{2} \right)"
            )
        )
        
        # Different coordinate pairs
        self.assertTrue(
            self.task._is_equiv(
                r"\left( 1, 2 \right)",
                r"\boxed{(1, 2)}"
            )
        )
        
        self.assertTrue(
            self.task._is_equiv(
                r"(5, 10)",
                r"\left( 5, 10 \right)"
            )
        )

    def test_is_equiv_left_right_removal(self):
        r"""Test that \left and \right are correctly removed (they're just formatting)."""
        # \left and \right should be ignored
        self.assertTrue(self.task._is_equiv(r"\left( 42 \right)", "42"))
        self.assertTrue(self.task._is_equiv(r"\left[ x \right]", "[x]"))
        self.assertTrue(self.task._is_equiv(r"\left\{ a \right\}", "{a}"))
        
        # Mixed formatting
        self.assertTrue(
            self.task._is_equiv(
                r"\left( \frac{1}{2} \right)",
                r"(\frac{1}{2})"
            )
        )

    def test_is_equiv_fractions_variants(self):
        """Test various fraction representations."""
        # \frac vs / vs decimal
        self.assertTrue(self.task._is_equiv(r"\frac{1}{2}", "1/2"))
        self.assertTrue(self.task._is_equiv(r"\frac{1}{2}", "0.5"))
        self.assertTrue(self.task._is_equiv(r"\frac{3}{4}", "3/4"))
        self.assertTrue(self.task._is_equiv(r"\frac{3}{4}", "0.75"))
        
        # \frac with variables
        self.assertTrue(self.task._is_equiv(r"\frac{x}{y}", "x/y"))
        self.assertTrue(self.task._is_equiv(r"\frac{\pi}{2}", "pi/2"))
        
        # Nested fractions
        self.assertTrue(
            self.task._is_equiv(
                r"\frac{1}{\frac{2}{3}}",
                "1/(2/3)"
            )
        )

    def test_is_equiv_math_symbols(self):
        """Test that common math symbols are normalized correctly."""
        # \pi normalization
        self.assertTrue(self.task._is_equiv(r"\pi", "pi"))
        self.assertTrue(self.task._is_equiv(r"2\pi", "2*pi"))
        self.assertTrue(self.task._is_equiv(r"\frac{\pi}{2}", "pi/2"))
        
        # Implicit multiplication with pi
        self.assertTrue(self.task._is_equiv(r"2\pi", "2*pi"))
        self.assertTrue(self.task._is_equiv(r"3\pi", "3*pi"))
        
        # Other Greek letters (if we add them)
        # Note: We currently only handle \pi, but this test documents expected behavior

    def test_is_equiv_complex_expressions(self):
        """Test more complex mathematical expressions."""
        # Simple algebraic expressions (commutative)
        self.assertTrue(self.task._is_equiv("2*x + 3*y", "3*y + 2*x"))
        
        # Algebraic simplifications - SymPy should handle these
        self.assertTrue(self.task._is_equiv("x^2 + 2*x + 1", "(x+1)^2"))
        self.assertTrue(self.task._is_equiv("(x+1)^2", "x^2 + 2*x + 1"))
        
        # More complex algebraic equivalences
        self.assertTrue(self.task._is_equiv("x^2 - 1", "(x-1)*(x+1)"))
        self.assertTrue(self.task._is_equiv("2*x + 2*y", "2*(x+y)"))

    def test_is_equiv_boxed_variants(self):
        """Test various \boxed{} formatting scenarios."""
        # Boxed with different content
        self.assertTrue(self.task._is_equiv(r"\boxed{42}", "42"))
        self.assertTrue(self.task._is_equiv(r"\boxed{\frac{1}{2}}", "1/2"))
        self.assertTrue(self.task._is_equiv(r"\boxed{(3, 4)}", "(3, 4)"))
        
        # Boxed in gold vs unboxed in prediction
        self.assertTrue(self.task._is_equiv("42", r"\boxed{42}"))
        self.assertTrue(self.task._is_equiv("1/2", r"\boxed{\frac{1}{2}}"))

    def test_is_equiv_whitespace_insensitive(self):
        """Test that whitespace doesn't affect equivalence."""
        self.assertTrue(self.task._is_equiv(" 42 ", "42"))
        self.assertTrue(self.task._is_equiv("x + y", "x+y"))
        self.assertTrue(self.task._is_equiv("( 3 , 4 )", "(3,4)"))
        self.assertTrue(
            self.task._is_equiv(
                r"\left( 3 , \frac{\pi}{2} \right)",
                r"(3,\pi/2)"
            )
        )

    def test_is_equiv_degrees(self):
        """Test that degree angle answers are normalized correctly."""
        # Various degree formats should all be equivalent
        self.assertTrue(self.task._is_equiv("72 degrees", "72"))
        self.assertTrue(self.task._is_equiv("72", "72 degrees"))
        self.assertTrue(self.task._is_equiv(r"72^\circ", "72"))
        self.assertTrue(self.task._is_equiv("72", r"72^\circ"))
        self.assertTrue(self.task._is_equiv(r"72^{\circ}", "72"))
        self.assertTrue(self.task._is_equiv("72 degrees", r"72^\circ"))
        self.assertTrue(self.task._is_equiv("45°", "45"))
        self.assertTrue(self.task._is_equiv("90 degrees", r"90^\circ"))
        
        # Different angles should NOT be equivalent
        self.assertFalse(self.task._is_equiv("72 degrees", "45 degrees"))

    def test_is_equiv_radians(self):
        """Test that radian angle answers are normalized correctly."""
        # Various radian formats should all be equivalent
        self.assertTrue(self.task._is_equiv(r"-\frac{\pi}{6} \text{radians}", r"-\frac{\pi}{6}"))
        self.assertTrue(self.task._is_equiv(r"-\frac{\pi}{6}", r"-\frac{\pi}{6} \text{radians}"))
        self.assertTrue(self.task._is_equiv(r"-\frac{\pi}{6} radians", r"-\frac{\pi}{6}"))
        self.assertTrue(self.task._is_equiv(r"-\frac{\pi}{6}", r"-\frac{\pi}{6} radians"))
        self.assertTrue(self.task._is_equiv(r"-\frac{\pi}{6} \text{radian}", r"-\frac{\pi}{6}"))
        self.assertTrue(self.task._is_equiv(r"\frac{\pi}{2} \text{radians}", r"\frac{\pi}{2}"))
        self.assertTrue(self.task._is_equiv(r"2\pi radians", "2*pi"))
        
        # Different angles should NOT be equivalent
        self.assertFalse(self.task._is_equiv(r"-\frac{\pi}{6} radians", r"\frac{\pi}{2} radians"))

    def test_is_equiv_text_stripping(self):
        """Test that \\text{...} commands are stripped (formatting-only)."""
        # \text{...} should be removed as it's formatting-only
        self.assertTrue(self.task._is_equiv(r"55 \text{answer}", "55"))
        self.assertTrue(self.task._is_equiv("55", r"55 \text{answer}"))
        self.assertTrue(self.task._is_equiv(r"72 \text{degrees}", "72"))
        self.assertTrue(self.task._is_equiv(r"100 \text{units}", "100"))

    def test_is_equiv_numeric_fallback(self):
        """Test numeric fallback for single-number answers with units."""
        # If each answer has exactly one number, compare those numbers
        # This handles cases like "55 cm²" vs "55" or "100 m²" vs "100"
        self.assertTrue(self.task._is_equiv("55 cm²", "55"))
        self.assertTrue(self.task._is_equiv("55", "55 cm²"))
        self.assertTrue(self.task._is_equiv("100 m²", "100"))
        self.assertTrue(self.task._is_equiv("3.14 cm", "3.14"))
        self.assertTrue(self.task._is_equiv("72 degrees", "72"))
        
        # Different numbers should NOT be equivalent
        self.assertFalse(self.task._is_equiv("55 cm²", "56"))
        self.assertFalse(self.task._is_equiv("100", "101 m²"))


if __name__ == "__main__":
    unittest.main()

