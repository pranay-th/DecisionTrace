// TypeScript types matching backend Pydantic schemas

export interface DecisionInput {
  title: string
  context: string
  constraints: string[]
  options: string[]
}

export interface StructuredDecision {
  decision_goal: string
  constraints: string[]
  options: string[]
  assumptions: string[]
  missing_information: string[]
}

export interface BiasReport {
  detected_biases: string[]
  evidence: Record<string, string>
  severity_score: number
}

export type ScenarioType = 'best_case' | 'worst_case' | 'most_likely'

export interface OutcomeScenario {
  scenario: ScenarioType
  description: string
  risks: string[]
  confidence: number
  timeframe_months: number
}

export interface OutcomeSimulation {
  scenarios: OutcomeScenario[]
}

export interface ReflectionInsight {
  accuracy_score: number
  lessons_learned: string[]
  repeated_patterns: string[]
}

export interface Decision {
  id: string
  created_at: string
  updated_at: string
  title: string
  context: string
  constraints: string[]
  options: string[]
  structured_decision: StructuredDecision
  bias_report: BiasReport
  outcome_simulations: OutcomeSimulation
  reflection_insight?: ReflectionInsight
  actual_outcome?: string
  execution_log: any[]
}

export interface DecisionListItem {
  id: string
  title: string
  created_at: string
  has_reflection: boolean
}
