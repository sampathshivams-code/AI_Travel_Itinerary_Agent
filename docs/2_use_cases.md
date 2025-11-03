# Use Case Analysis

## Simple Use Case: Budget-Based Itinerary Planning

### Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant IA as Itinerary Agent
    participant P as Planner
    participant BA as Budget Agent
    participant D as Data Store

    U->>IA: Request Itinerary (budget, people, nights)
    IA->>BA: Validate Budget
    BA-->>IA: Budget Validated
    
    IA->>P: Plan Itinerary
    P->>D: Get Transport Options
    D-->>P: Transport Data
    P->>D: Get Accommodation Options
    D-->>P: Accommodation Data
    P->>D: Get Activity Options
    D-->>P: Activity Data
    
    P-->>IA: Initial Plan
    IA->>BA: Verify Total Cost
    BA-->>IA: Cost Verified
    
    IA-->>U: Present Itinerary
```

### Description

1. **Initial Request**
   - User provides budget, number of people, and nights
   - System validates input parameters

2. **Budget Validation**
   - Budget Agent checks minimum feasibility
   - Validates per-person and per-night constraints

3. **Resource Selection**
   - Planner queries available options
   - Applies budget allocation heuristics
   - Optimizes for value within constraints

4. **Plan Creation**
   - Transport selection (40% budget)
   - Accommodation selection (40% budget)
   - Activity selection (20% budget)

5. **Verification**
   - Budget Agent verifies total costs
   - Confirms plan feasibility

6. **Response**
   - Returns complete itinerary
   - Includes cost breakdown
   - Indicates feasibility status

## Advanced Use Case: Weather-Triggered Replanning

### Flow Diagram

```mermaid
sequenceDiagram
    participant WA as Weather Agent
    participant MB as Message Bus
    participant IA as Itinerary Agent
    participant AS as Activity Scorer
    participant R as Replanner
    participant U as User

    WA->>MB: Publish Weather Alert
    MB->>IA: Weather Alert Notification
    
    IA->>AS: Request Activity Scoring
    AS->>IA: Activity Scores
    
    IA->>R: Request Replanning
    R->>AS: Get Replacement Options
    AS-->>R: Scored Replacements
    
    R-->>IA: Updated Plan
    IA->>MB: Publish Plan Update
    MB->>U: Notification
```

### Description

1. **Weather Monitoring**
   - Weather Agent detects poor conditions
   - Alert published to Message Bus
   - Affected activities identified

2. **Impact Analysis**
   - Itinerary Agent receives alert
   - Determines affected timeframes
   - Identifies activities needing changes

3. **Replacement Scoring**
   - Activity Scorer evaluates options
   - Considers:
     - Indoor/outdoor status
     - Cost constraints
     - Activity similarity
     - Value optimization

4. **Plan Adjustment**
   - Replanner generates alternatives
   - Maintains budget constraints
   - Preserves schedule feasibility
   - Optimizes for minimal disruption

5. **User Notification**
   - Changes communicated to user
   - Explains weather impact
   - Shows cost implications
   - Presents alternative activities

### Success Criteria

1. **Simple Use Case**
   - Plan within budget
   - Reasonable cost allocation
   - Maximum value activities
   - Fast execution (<1s)

2. **Advanced Use Case**
   - Quick response to weather
   - Suitable indoor alternatives
   - Budget maintenance
   - Minimal disruption
   - Clear user communication