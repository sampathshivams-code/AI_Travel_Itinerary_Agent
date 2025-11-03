"""Deterministic sample data for the itinerary agent.

Keep data simple and self-contained so the prototype runs without external APIs.
"""

TRANSPORT_OPTIONS = [
    {
        "id": "flight_economy",
        "type": "flight",
        "name": "Flight (Economy)",
        "cost_per_person": 8000,
        "duration_hours": 2
    },
    {
        "id": "flight_premium",
        "type": "flight",
        "name": "Flight (Premium Economy)",
        "cost_per_person": 12000,
        "duration_hours": 2
    },
    {
        "id": "road_bus",
        "type": "road",
        "name": "Bus",
        "cost_per_person": 1500,
        "duration_hours": 10
    },
    {
        "id": "road_car",
        "type": "road",
        "name": "Private Car (shared)",
        "cost_per_person": 4000,
        "duration_hours": 6
    }
]

ACCOMMODATION_OPTIONS = [
    {
        "id": "hostel",
        "category": "budget",
        "name": "Hostel",
        "cost_per_night": 1000,
        "comfort_score": 3
    },
    {
        "id": "guesthouse",
        "category": "mid",
        "name": "Guest House",
        "cost_per_night": 2500,
        "comfort_score": 6
    },
    {
        "id": "resort",
        "category": "premium",
        "name": "Resort",
        "cost_per_night": 8000,
        "comfort_score": 9
    }
]

ACTIVITIES = [
    {"id": "beach_visit", "name": "Beach Visit", "cost": 0, "score": 5, "type": "outdoor"},
    {"id": "water_sports", "name": "Water Sports", "cost": 3000, "score": 8, "type": "outdoor"},
    {"id": "spa", "name": "Spa Session", "cost": 2500, "score": 6, "type": "indoor"},
    {"id": "museums", "name": "Local Museums", "cost": 500, "score": 4, "type": "indoor"},
    {"id": "boat_cruise", "name": "Boat Cruise", "cost": 2000, "score": 7, "type": "outdoor"},
    {"id": "food_tour", "name": "Local Food Tour", "cost": 1500, "score": 6, "type": "indoor"}
]
