"""Activity scoring and replacement logic.

This module handles the logic for scoring activities and finding suitable replacements
when weather or other events require changes to the itinerary.
"""
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

def calculate_similarity(activity1: Dict[str, Any], activity2: Dict[str, Any]) -> float:
    """Calculate similarity score between two activities based on type, cost, and score."""
    # Cost similarity (0-1): closer costs = higher similarity
    max_cost_diff = 3000  # normalize cost differences
    cost_similarity = max(0, 1 - abs(activity1["cost"] - activity2["cost"]) / max_cost_diff)
    
    # Score similarity (0-1): closer scores = higher similarity
    max_score_diff = 10  # assuming scores are 0-10
    score_similarity = max(0, 1 - abs(activity1["score"] - activity2["score"]) / max_score_diff)
    
    # Type match bonus
    type_bonus = 1.0 if activity1["type"] == activity2["type"] else 0.0
    
    # Weighted combination
    similarity = (0.3 * cost_similarity + 
                 0.3 * score_similarity + 
                 0.4 * type_bonus)
    
    return similarity

def score_activity_replacement(original: Dict[str, Any], 
                             candidate: Dict[str, Any],
                             target_type: str = "indoor") -> float:
    """Score how good a replacement candidate is for the original activity."""
    if candidate["id"] == original["id"]:
        return 0.0  # Don't replace with same activity
        
    # Base score from similarity
    similarity = calculate_similarity(original, candidate)
    
    # Type matching score
    type_match = 1.0 if candidate["type"] == target_type else 0.0
    
    # Value score (higher score/cost ratio is better)
    value_score = candidate["score"] / (candidate["cost"] + 1)  # add 1 to avoid division by zero
    max_value = 10  # normalize value score
    normalized_value = min(value_score / max_value, 1.0)
    
    # Weighted combination
    final_score = (0.4 * similarity +  # similarity to original
                  0.4 * type_match +   # matches required type
                  0.2 * normalized_value)  # good value for money
                  
    return final_score

def find_replacement_activities(activities: List[Dict[str, Any]], 
                              all_activities: List[Dict[str, Any]],
                              target_type: str = "indoor",
                              budget: Optional[float] = None) -> List[Dict[str, Any]]:
    """Find replacement activities of the target type that fit within budget."""
    replacements = []
    remaining_budget = budget if budget is not None else float('inf')
    
    # Process one activity at a time to maintain budget constraints
    for original in activities:
        if original["type"] == target_type:
            # Keep activities that are already the target type
            replacements.append(original)
            remaining_budget -= original["cost"]
            continue
            
        # Score all possible replacements
        candidates = [
            (a, score_activity_replacement(original, a, target_type))
            for a in all_activities
            if a["cost"] <= remaining_budget
        ]
        
        # Sort by score and pick the best that fits budget
        candidates.sort(key=lambda x: -x[1])  # Sort by score descending
        
        if candidates:
            best = candidates[0][0]
            replacements.append(best)
            remaining_budget -= best["cost"]
            logger.info(
                "Replacing activity %s with %s (score: %.2f)", 
                original["id"], 
                best["id"], 
                candidates[0][1]
            )
        else:
            logger.warning(
                "No suitable replacement found for activity %s within budget %s",
                original["id"],
                remaining_budget
            )
            # Keep original if no replacement found
            replacements.append(original)
            remaining_budget -= original["cost"]
            
    return replacements