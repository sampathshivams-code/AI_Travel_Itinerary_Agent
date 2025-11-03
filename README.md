# Agentic AI Travel Planner

An intelligent travel planning system that creates and dynamically adjusts itineraries based on budget constraints, weather conditions, and external events. Uses a multi-agent architecture to handle replanning and coordination.

## Features

1. **Budget-based Planning**
   - Optimizes transport, accommodation, and activities within budget
   - Smart upgrades when budget allows
   - Value-based activity selection

2. **Dynamic Replanning**
   - Handles flight delays with smart adjustments
   - Weather-triggered indoor activity substitution
   - Multi-night stay adjustments

3. **Multi-Agent System**
   - Itinerary Agent: Central coordinator
   - Weather Agent: Monitors conditions
   - Event Agent: Handles delays/closures
   - Budget Agent: Tracks spending
   - Message bus for coordination

4. **Activity Scoring**
   - Similarity-based replacement
   - Type matching (indoor/outdoor)
   - Value optimization

## Project Structure

```
.
├── docs/                    # Design documentation
│   ├── 1_system_architecture.md
│   ├── 2_use_cases.md
│   └── 3_peas_and_agents.md
├── src/                     # Source code
│   ├── activity_scorer.py   # Activity scoring/replacement logic
│   ├── agent_demo.py       # Multi-agent simulation demo
│   ├── agents.py           # Agent implementations
│   ├── data.py            # Sample travel data
│   ├── logging_config.py   # Logging setup
│   ├── planner.py         # Core planning logic
│   ├── replanner.py       # Dynamic replanning
│   └── run_budgets.py     # Budget comparison tool
├── tests/                  # Unit tests
│   ├── test_activity_scorer.py
│   ├── test_agents.py
│   ├── test_planner.py
│   └── test_replanner.py
├── cli.py                 # Command-line interface
└── requirements.txt       # Python dependencies
```

## Quick Start

1. Set up Python environment (3.8+ recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

2. Run basic planning demo:
```bash
python cli.py --budget 25000 --people 2 --nights 3
```

3. Try replanning scenarios:
```bash
# Simulate flight delay
python cli.py --budget 20000 --people 1 --nights 2 --delay 5

# Run multi-agent demo
python cli.py --budget 18000 --people 1 --nights 2 --demo
```

4. Compare different budgets:
```bash
# Run with multiple budgets and save CSV
python src/run_budgets.py --csv comparison.csv 5000 10000 18000 30000
```

## Testing

Run all tests:
```bash
python -m unittest discover -v
```

Run specific test suites:
```bash
python -m unittest tests.test_planner -v
python -m unittest tests.test_replanner -v
python -m unittest tests.test_agents -v
python -m unittest tests.test_activity_scorer -v
```

## Design Documentation

- [System Architecture](docs/1_system_architecture.md)
- [Use Cases](docs/2_use_cases.md)
- [PEAS Analysis & Agents](docs/3_peas_and_agents.md)

## Implementation Notes

1. **Data Model**
   - Uses static sample data for quick prototyping
   - Structured for future API integration
   - Includes transport, accommodation, and activity options

2. **Planning Strategy**
   - Initial budget allocation: 40% transport, 40% accommodation, 20% activities
   - Upgrades attempted when budget allows
   - Fallback to cheaper options when needed

3. **Replanning Logic**
   - Preserves as much of original plan as possible
   - Considers faster transport options for delays
   - Smart activity substitution based on type and value

4. **Agent Communication**
   - Asynchronous message bus
   - Event-driven architecture
   - Loose coupling between components

## Future Enhancements

1. **External Integration**
   - Real weather API
   - Flight booking systems
   - Hotel availability APIs
   - Real-time pricing

2. **Advanced Features**
   - Machine learning for preferences
   - Predictive weather planning
   - Multi-city itineraries
   - Group coordination

3. **Technical Improvements**
   - Distributed agent system
   - Real-time monitoring
   - Mobile interface
   - Booking integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
