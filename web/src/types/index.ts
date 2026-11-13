export type OwaspCategory =
  | 'ASI01'
  | 'ASI02'
  | 'ASI03'
  | 'ASI04'
  | 'ASI05'
  | 'ASI06'
  | 'ASI07'
  | 'ASI08'
  | 'ASI09'
  | 'ASI10';

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFORMATIONAL';

export type RiskGrade = 'A' | 'B' | 'C' | 'D' | 'F';

export interface AttackStep {
  step_id: string;
  step_type: string;
  content: string;
  tool_name?: string;
  call_id?: string;
}

export interface CanaryCondition {
  type: string;
  target_name?: string;
  expected_token?: string;
  regex_pattern?: string;
  description?: string;
}

export interface Scenario {
  id: string;
  name: string;
  category: OwaspCategory;
  severity: Severity;
  description: string;
  setup?: Record<string, any>;
  attack_steps: AttackStep[];
  canaries: CanaryCondition[];
  remediation_hint: string;
  tags: string[];
}

export interface TargetSpec {
  id?: string;
  name: string;
  type: 'in_process' | 'subprocess' | 'http' | 'websocket';
  endpoint: string;
  mode: 'vulnerable' | 'hardened';
  timeout_sec: number;
}

export interface RunConfig {
  target_spec: TargetSpec;
  selected_categories: OwaspCategory[];
  selected_scenarios: string[];
  trials_per_scenario: number;
  seed: number;
  max_budget_steps: number;
  max_budget_time_sec: number;
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, any>;
}

export interface TranscriptEntry {
  role: string;
  content: string;
  tool_calls?: ToolCall[];
  timestamp?: string;
}

export interface Finding {
  id: string;
  scenario_id: string;
  scenario_name: string;
  category: OwaspCategory;
  severity: Severity;
  trials_run: number;
  successful_attacks: number;
  attack_success_rate: number;
  wilson_lower: number;
  wilson_upper: number;
  canary_summary: string;
  remediation_hint: string;
  sample_transcript: TranscriptEntry[];
}

export interface CategoryScore {
  category: OwaspCategory;
  category_name: string;
  total_scenarios: number;
  total_trials: number;
  successful_attacks: number;
  attack_success_rate: number;
  wilson_lower: number;
  wilson_upper: number;
  findings_count: number;
}

export interface RunSummary {
  run_id: string;
  target_name: string;
  target_mode: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  total_scenarios: number;
  total_trials: number;
  successful_attacks: number;
  overall_asr: number;
  wilson_lower: number;
  wilson_upper: number;
  risk_grade: RiskGrade;
  category_scores: CategoryScore[];
  findings: Finding[];
  duration_ms: number;
  started_at: string;
  completed_at?: string;
  error?: string;
}

export interface RunComparison {
  baseline_run_id: string;
  hardened_run_id: string;
  baseline_target: string;
  hardened_target: string;
  baseline_asr: number;
  hardened_asr: number;
  asr_delta: number;
  baseline_grade: RiskGrade;
  hardened_grade: RiskGrade;
  resolved_scenarios: string[];
  persistent_scenarios: string[];
  category_deltas: Record<string, number>;
}
