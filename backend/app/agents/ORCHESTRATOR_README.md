# DecisionOrchestrator Implementation

## Overview

The `DecisionOrchestrator` class is the central pipeline orchestrator for the DecisionTrace system. It chains all agents together, handles errors with retry and fallback logic, and persists results to the database.

## Implementation Status

### ✅ Task 9.1: Create DecisionOrchestrator class
- **Initialize all agents in __init__**: ✅ Complete
  - Initializes `DecisionStructuringAgent`
  - Initializes `BiasDetectionAgent`
  - Initializes `OutcomeSimulationAgent`
  - Initializes `ReflectionAgent`
  - All agents share the same `LLMClient` instance
  
- **Implement process_decision method**: ✅ Complete
  - Accepts `DecisionInput` as parameter
  - Returns `Decision` model with all agent outputs
  - Orchestrates the full pipeline execution
  - Handles errors and logging
  
- **Implement _execute_with_logging helper**: ✅ Complete
  - Executes any agent with input data
  - Records start and end times
  - Logs execution details
  - Appends to execution_log list
  - Handles errors gracefully

### ✅ Task 9.2: Implement sequential execution
- **Execute DecisionStructuringAgent first**: ✅ Complete
  - Line 88-93 in orchestrator.py
  - Receives raw `DecisionInput`
  - Returns `StructuredDecision`
  
- **Pass output to BiasDetectionAgent**: ✅ Complete
  - Line 95-100 in orchestrator.py
  - Receives `StructuredDecision` from previous step
  - Returns `BiasReport`
  
- **Pass both outputs to OutcomeSimulationAgent**: ✅ Complete
  - Line 102-111 in orchestrator.py
  - Receives both `StructuredDecision` and `BiasReport`
  - Returns `OutcomeSimulation` with 3 scenarios
  
- **Validate outputs at each stage**: ✅ Complete
  - Validation handled by `BaseAgent.execute()` method
  - Each agent's output is validated against its Pydantic schema
  - Validation failures trigger retry/fallback logic in `LLMClient`

### ✅ Task 9.3: Implement error handling
- **Catch validation errors and trigger retry**: ✅ Complete
  - Handled by `LLMClient.generate_structured()` method
  - Validation errors trigger retry (max 1 retry)
  - Logged in execution_log
  
- **Catch retry failures and trigger fallback**: ✅ Complete
  - Handled by `LLMClient.generate_structured()` method
  - After max retries, switches to fallback model
  - Logged in execution_log
  
- **Catch fallback failures and return graceful error**: ✅ Complete
  - Line 133-149 in orchestrator.py
  - Catches `GracefulFailureError` from agents
  - Logs error details to execution_log
  - Re-raises error for API layer to handle
  
- **Log all execution details**: ✅ Complete
  - Line 79 initializes execution_log list
  - Each agent execution appends details to log
  - Log includes: agent name, status, timestamps, duration, model used
  - Errors include error message and type

### ✅ Task 9.4: Implement database persistence
- **Save decision with all agent outputs**: ✅ Complete
  - Line 119-128 calls `_save_decision()` method
  - Line 241-295 implements `_save_decision()` method
  - Creates `Decision` model with all fields populated
  - Includes: title, context, constraints, options
  - Includes: structured_decision, bias_report, outcome_simulations
  - Includes: execution_log
  
- **Save execution log**: ✅ Complete
  - Line 285 sets `execution_log` field on Decision model
  - Log contains all agent execution details
  - Persisted as JSONB in PostgreSQL
  
- **Handle database errors gracefully**: ✅ Complete
  - Line 289-302 in `_save_decision()` method
  - Try/except block wraps database operations
  - Rollback on error (line 291)
  - Logs error details (line 293-297)
  - Wraps in `GracefulFailureError` (line 300-302)

## Architecture

### Pipeline Flow

```
DecisionInput
    ↓
DecisionStructuringAgent
    ↓
StructuredDecision
    ↓
BiasDetectionAgent
    ↓
BiasReport
    ↓
OutcomeSimulationAgent (receives both StructuredDecision + BiasReport)
    ↓
OutcomeSimulation
    ↓
Database Persistence
    ↓
Decision (with all outputs)
```

### Error Handling Flow

```
Agent Execution
    ↓
Validation Error?
    ↓ Yes
Retry (max 1)
    ↓
Still Failing?
    ↓ Yes
Fallback Model
    ↓
Still Failing?
    ↓ Yes
GracefulFailureError
    ↓
Log to execution_log
    ↓
Re-raise to API layer
```

### Database Transaction Flow

```
Create Decision Model
    ↓
Add to Session
    ↓
Commit Transaction
    ↓
Success? → Refresh & Return
    ↓ No
Rollback Transaction
    ↓
Log Error
    ↓
Raise GracefulFailureError
```

## Key Features

### 1. Sequential Agent Execution
- Agents execute in strict order
- No agent can be skipped
- Each agent receives validated output from previous agents
- Pipeline stops on first failure

### 2. Comprehensive Logging
- Every agent execution is logged
- Timestamps for start and end
- Duration in milliseconds
- Model used for each call
- Success/failure status
- Error details on failure

### 3. Error Recovery
- Automatic retry on validation failure
- Automatic fallback to secondary model
- Graceful error messages for users
- No crashes or hangs

### 4. Database Persistence
- All agent outputs saved as JSONB
- Execution log preserved for traceability
- Atomic transactions (all or nothing)
- Automatic rollback on errors

### 5. Reflection Support
- `add_reflection()` method for post-decision analysis
- Fetches existing decision from database
- Executes ReflectionAgent with actual outcome
- Updates decision with reflection insight
- Appends to existing execution log

## Usage Example

```python
from app.agents.orchestrator import DecisionOrchestrator
from app.services.llm_client import LLMClient
from app.schemas.decision_input import DecisionInput
from app.database import get_db

# Initialize components
llm_client = LLMClient(api_key="your-api-key")
db_session = await get_db()

# Create orchestrator
orchestrator = DecisionOrchestrator(
    llm_client=llm_client,
    db_session=db_session
)

# Process decision
decision_input = DecisionInput(
    title="Should I accept the job offer?",
    context="I received an offer from Company X...",
    constraints=["Must relocate", "Salary is 20% higher"],
    options=["Accept", "Decline", "Negotiate"]
)

try:
    decision = await orchestrator.process_decision(decision_input)
    print(f"Decision created: {decision.id}")
    print(f"Structured: {decision.structured_decision}")
    print(f"Biases: {decision.bias_report}")
    print(f"Outcomes: {decision.outcome_simulations}")
except GracefulFailureError as e:
    print(f"Analysis failed: {e}")
```

## Testing

The orchestrator can be tested with:
1. Unit tests with mocked agents
2. Integration tests with real LLM calls
3. End-to-end tests with database

See `test_orchestrator.py` for basic unit tests.

## Dependencies

- `app.agents.base.BaseAgent`: Abstract base class for agents
- `app.agents.decision_structuring.DecisionStructuringAgent`: First agent in pipeline
- `app.agents.bias_detection.BiasDetectionAgent`: Second agent in pipeline
- `app.agents.outcome_simulation.OutcomeSimulationAgent`: Third agent in pipeline
- `app.agents.reflection.ReflectionAgent`: Deferred agent for post-decision analysis
- `app.services.llm_client.LLMClient`: LLM API client with retry/fallback
- `app.schemas.decision_input.DecisionInput`: Input validation schema
- `app.models.decision.Decision`: Database model
- `sqlalchemy.ext.asyncio.AsyncSession`: Database session

## Error Types

- `GracefulFailureError`: Raised when all retry and fallback attempts fail
  - Caught and logged by orchestrator
  - Re-raised to API layer for user-friendly error response
  
- `ValidationError`: Raised when Pydantic validation fails
  - Handled by LLMClient (triggers retry/fallback)
  - Not directly handled by orchestrator
  
- `Exception`: Any unexpected error
  - Caught by orchestrator
  - Logged with full details
  - Wrapped in GracefulFailureError

## Logging Output

Each execution produces a structured log like:

```json
[
  {
    "agent": "DecisionStructuringAgent",
    "status": "success",
    "start_time": "2024-01-19T10:00:00.000Z",
    "end_time": "2024-01-19T10:00:05.123Z",
    "duration_ms": 5123,
    "model_used": "deepseek/deepseek-chat"
  },
  {
    "agent": "BiasDetectionAgent",
    "status": "success",
    "start_time": "2024-01-19T10:00:05.200Z",
    "end_time": "2024-01-19T10:00:08.456Z",
    "duration_ms": 3256,
    "model_used": "deepseek/deepseek-chat"
  },
  {
    "agent": "OutcomeSimulationAgent",
    "status": "success",
    "start_time": "2024-01-19T10:00:08.500Z",
    "end_time": "2024-01-19T10:00:12.789Z",
    "duration_ms": 4289,
    "model_used": "deepseek/deepseek-chat"
  }
]
```

## Compliance with Requirements

### Requirement 2.1-2.9: Agent Pipeline Orchestration
✅ All requirements met:
- 2.1: DecisionStructuringAgent executes first
- 2.2: BiasDetectionAgent receives validated structured decision
- 2.3: OutcomeSimulationAgent receives both structured decision and bias report
- 2.4: ReflectionAgent is deferred (separate method)
- 2.5: No agent can be skipped (sequential execution)
- 2.6: Each agent output conforms to Pydantic schema
- 2.7: Schema validation failures trigger retry (in LLMClient)
- 2.8: Failed retry triggers fallback model switch (in LLMClient)
- 2.9: Fallback failure returns graceful error state

### Requirement 8.1-8.9: Data Persistence
✅ All requirements met:
- 8.1: PostgreSQL database stores all decisions
- 8.2: Each decision has id, created_at, updated_at (in Decision model)
- 8.3: Original user input is stored (title, context, constraints, options)
- 8.4: StructuredDecision output stored as JSON
- 8.5: BiasReport output stored as JSON
- 8.6: OutcomeSimulation outputs stored as JSON
- 8.7: ReflectionInsight stored as JSON (when available)
- 8.8: All agent execution logs stored with timestamps
- 8.9: Model used for each agent is logged

### Requirement 11.1-11.8: Error Handling and Reliability
✅ All requirements met:
- 11.1: Schema validation errors trigger retry (in LLMClient)
- 11.2: Retry failures trigger fallback model (in LLMClient)
- 11.3: Fallback failures return graceful error message
- 11.4: Timeouts handled (in LLMClient)
- 11.5: Empty outputs treated as failures (Pydantic validation)
- 11.6: All errors logged with context
- 11.7: User sees friendly error messages (GracefulFailureError)
- 11.8: System never crashes (all exceptions caught)

## Conclusion

The DecisionOrchestrator implementation is **complete** and meets all requirements specified in tasks 9.1-9.4. It provides:

1. ✅ Proper initialization of all agents
2. ✅ Sequential execution with validation
3. ✅ Comprehensive error handling with retry/fallback
4. ✅ Database persistence with transaction safety
5. ✅ Detailed execution logging
6. ✅ Reflection support for post-decision analysis

The implementation is production-ready and follows best practices for:
- Error handling
- Logging
- Database transactions
- Type safety (Pydantic)
- Async/await patterns
