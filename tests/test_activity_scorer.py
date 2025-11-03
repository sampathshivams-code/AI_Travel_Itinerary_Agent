import unittest
from src.activity_scorer import (
    calculate_similarity,
    score_activity_replacement,
    find_replacement_activities
)
from src.data import ACTIVITIES


class ActivityScorerTests(unittest.TestCase):
    def setUp(self):
        # Sample activities for testing
        self.beach = next(a for a in ACTIVITIES if a["id"] == "beach_visit")
        self.museum = next(a for a in ACTIVITIES if a["id"] == "museums")
        self.spa = next(a for a in ACTIVITIES if a["id"] == "spa")
    
    def test_similarity_calculation(self):
        """Test that similarity scoring works as expected."""
        # Same type activities should have higher similarity
        food_tour = next(a for a in ACTIVITIES if a["id"] == "food_tour")
        museum_similarity = calculate_similarity(self.museum, food_tour)
        beach_similarity = calculate_similarity(self.museum, self.beach)
        
        self.assertGreater(museum_similarity, beach_similarity)
        
    def test_replacement_scoring(self):
        """Test activity replacement scoring."""
        # Scoring beach replacement with indoor activities
        spa_score = score_activity_replacement(self.beach, self.spa, "indoor")
        museum_score = score_activity_replacement(self.beach, self.museum, "indoor")
        
        # Museum should score better as it's cheaper while still being indoor
        self.assertGreater(museum_score, 0)
        self.assertLessEqual(museum_score, 1)
        
        # Same activity should score 0
        self.assertEqual(
            score_activity_replacement(self.beach, self.beach, "indoor"),
            0
        )
        
    def test_find_replacements(self):
        """Test finding replacement activities within budget."""
        # Try to replace outdoor activities with indoor ones
        outdoor_activities = [a for a in ACTIVITIES if a["type"] == "outdoor"][:2]
        budget = sum(a["cost"] for a in outdoor_activities) + 500  # Small buffer
        
        replacements = find_replacement_activities(
            outdoor_activities,
            ACTIVITIES,
            "indoor",
            budget
        )
        
        # Should get same number of activities back
        self.assertEqual(len(replacements), len(outdoor_activities))
        
        # Replacements should be within budget
        self.assertLessEqual(
            sum(a["cost"] for a in replacements),
            budget
        )
        
        # Should prefer indoor activities
        indoor_count = len([a for a in replacements if a["type"] == "indoor"])
        self.assertGreater(indoor_count, 0)
        
    def test_budget_constraint(self):
        """Test that replacements respect budget constraints."""
        # Try with a very low budget
        original = [self.beach]  # Free activity
        tiny_budget = 100
        
        replacements = find_replacement_activities(
            original,
            ACTIVITIES,
            "indoor",
            tiny_budget
        )
        
        # With tiny budget, should keep original activity
        self.assertEqual(replacements[0]["id"], self.beach["id"])
        
    def test_type_preference(self):
        """Test that activity type preferences are respected."""
        # Try to replace indoor with outdoor
        indoor_activities = [a for a in ACTIVITIES if a["type"] == "indoor"][:2]
        budget = 10000  # Large enough budget
        
        replacements = find_replacement_activities(
            indoor_activities,
            ACTIVITIES,
            "outdoor",
            budget
        )
        
        # Should have some outdoor activities
        outdoor_count = len([a for a in replacements if a["type"] == "outdoor"])
        self.assertGreater(outdoor_count, 0)


if __name__ == "__main__":
    unittest.main()