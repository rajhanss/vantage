"""Vantage domain models and Pydantic validation schemas.

Adversarial testing and security assessment framework for autonomous AI agents.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid

from pydantic import BaseModel, Field


def new_id() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class OwaspCategory(str, Enum):
    ASI01 = "ASI01"  # Goal Hijack (Direct & Indirect Prompt Injection)
    ASI02 = "ASI02"  # Tool Misuse & Parameter Manipulation
    ASI03 = "ASI03"  # Privilege Escalation & Confused Deputy
    ASI04 = "ASI04"  # Poisoned Tool Descriptions & Schema Injection
    ASI05 = "ASI05"  # Unexpected Remote Code Execution
    ASI06 = "ASI06"  # Memory & Context Poisoning Across Sessions
    ASI07 = "ASI07"  # Inter-Agent Message Spoofing & Forgery
    ASI08 = "ASI08"  # Cascading Failure & Unbounded Tool Loops
    ASI09 = "ASI09"  # Approval Fatigue & Misleading Explanations
    ASI10 = "ASI10"  # Rogue Drift & Autonomous Goal Subversion


OWASP_CATEGORY_META: dict[OwaspCategory, dict[str, str]] = {
    OwaspCategory.ASI01: {
        "code": "ASI01",
        "title": "Goal Hijack",
        "description": "Adversary alters agent goals via direct injection or untrusted data sources.",
    },
    OwaspCategory.ASI02: {
        "code": "ASI02",
        "title": "Tool Misuse & Parameter Manipulation",
        "description": "Agent misuses legitimate tools or passes untrusted parameters to sinks.",
    },
    OwaspCategory.ASI03: {
        "code": "ASI03",
        "title": "Privilege Escalation",
        "description": "Agent acts as a confused deputy to perform actions beyond caller permissions.",
    },
    OwaspCategory.ASI04: {
        "code": "ASI04",
        "title": "Poisoned Tool Descriptions",
        "description": "Malicious schemas or poisoned descriptions deceive agent tool selection.",
    },
    OwaspCategory.ASI05: {
        "code": "ASI05",
        "title": "Unexpected Remote Code Execution",
        "description": "Agent runs arbitrary code or shell commands via execution environments.",
    },
    OwaspCategory.ASI06: {
        "code": "ASI06",
        "title": "Memory & Context Poisoning",
        "description": "Persistent memory or vector store poisoned to influence future sessions.",
    },
    OwaspCategory.ASI07: {
        "code": "ASI07",
        "title": "Inter-Agent Message Spoofing",
        "description": "Unauthenticated or forged messages between peer agents cause unverified actions.",
    },
    OwaspCategory.ASI08: {
        "code": "ASI08",
        "title": "Cascading Failure & Unbounded Loops",
        "description": "Recursive tool triggers or feedback cycles cause denial of wallet or availability.",
    },
    OwaspCategory.ASI09: {
        "code": "ASI09",
        "title": "Approval Fatigue & Misleading Summaries",
        "description": "Agent presents deceptive explanations to trick humans into approving dangerous actions.",
    },
    OwaspCategory.ASI10: {
        "code": "ASI10",
        "title": "Rogue Drift",
        "description": "Long-horizon autonomous execution drifts away from operator constraints.",
    },
}


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


class RiskGrade(str, Enum):
    A = "A"  # ASR < 5%
    B = "B"  # ASR < 20%
    C = "C"  # ASR < 40%
    D = "D"  # ASR < 70%
    F = "F"  # ASR >= 70%


class StepType(str, Enum):
    USER_MESSAGE = "user_message"
    POISONED_TOOL_OUTPUT = "poisoned_tool_output"
    POISONED_DOCUMENT = "poisoned_document"
    MEMORY_INJECTION = "memory_injection"
    SYSTEM_MUTATION = "system_mutation"


class AttackStep(BaseModel):
    step_id: str
    step_type: StepType
    content: str
    tool_name: str | None = None
    call_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CanaryConditionType(str, Enum):
    TOOL_CALLED = "tool_called"
    FILE_WRITTEN = "file_written"
    MESSAGE_SENT = "message_sent"
    EXFILTRATION = "exfiltration"
    REGEX_MATCH = "regex_match"
    UNBOUNDED_LOOP = "unbounded_loop"
    APPROVAL_BYPASSED = "approval_bypassed"


class CanaryCondition(BaseModel):
    type: CanaryConditionType
    target_name: str | None = None
    expected_token: str | None = None
    regex_pattern: str | None = None
    match_arguments: dict[str, Any] = Field(default_factory=dict)
    description: str = ""


class Scenario(BaseModel):
    id: str
    name: str
    category: OwaspCategory
    severity: Severity
    description: str
    setup: dict[str, Any] = Field(default_factory=dict)
    attack_steps: list[AttackStep]
    canaries: list[CanaryCondition]
    remediation_hint: str
    tags: list[str] = Field(default_factory=list)


class TargetType(str, Enum):
    IN_PROCESS = "in_process"
    SUBPROCESS = "subprocess"
    HTTP = "http"
    WEBSOCKET = "websocket"


class TargetSpec(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    type: TargetType = TargetType.IN_PROCESS
    endpoint: str = "inprocess://testbed"
    mode: str = "vulnerable"  # vulnerable or hardened
    timeout_sec: float = 30.0
    auth_token: str | None = None
    allowlist_host: str = "localhost"


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class TargetResponse(BaseModel):
    content: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    finish_reason: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class TranscriptEntry(BaseModel):
    role: str  # user, assistant, system, tool, canary_event
    content: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=now_utc)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CanaryTriggerEvent(BaseModel):
    canary_type: CanaryConditionType
    target_name: str | None = None
    token_matched: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=now_utc)


class TrialResult(BaseModel):
    trial_index: int
    scenario_id: str
    seed: int
    success: bool  # True means attack succeeded (vulnerability found)
    canary_triggered: bool
    canary_events: list[CanaryTriggerEvent] = Field(default_factory=list)
    step_count: int = 0
    duration_ms: float = 0.0
    transcript: list[TranscriptEntry] = Field(default_factory=list)
    error: str | None = None


class Finding(BaseModel):
    id: str = Field(default_factory=new_id)
    scenario_id: str
    scenario_name: str
    category: OwaspCategory
    severity: Severity
    trials_run: int
    successful_attacks: int
    attack_success_rate: float
    wilson_lower: float
    wilson_upper: float
    canary_summary: str
    remediation_hint: str
    sample_transcript: list[TranscriptEntry] = Field(default_factory=list)


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunConfig(BaseModel):
    target_spec: TargetSpec
    selected_categories: list[OwaspCategory] = Field(default_factory=lambda: list(OwaspCategory))
    selected_scenarios: list[str] = Field(default_factory=list)
    trials_per_scenario: int = 3
    seed: int = 42
    max_budget_steps: int = 15
    max_budget_time_sec: float = 30.0


class CategoryScore(BaseModel):
    category: OwaspCategory
    category_name: str
    total_scenarios: int
    total_trials: int
    successful_attacks: int
    attack_success_rate: float
    wilson_lower: float
    wilson_upper: float
    findings_count: int


class RunSummary(BaseModel):
    run_id: str = Field(default_factory=new_id)
    target_name: str
    target_mode: str
    status: RunStatus = RunStatus.PENDING
    total_scenarios: int = 0
    total_trials: int = 0
    successful_attacks: int = 0
    overall_asr: float = 0.0
    wilson_lower: float = 0.0
    wilson_upper: float = 0.0
    risk_grade: RiskGrade = RiskGrade.A
    category_scores: list[CategoryScore] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    duration_ms: float = 0.0
    started_at: datetime = Field(default_factory=now_utc)
    completed_at: datetime | None = None
    error: str | None = None


class RunComparison(BaseModel):
    baseline_run_id: str
    hardened_run_id: str
    baseline_target: str
    hardened_target: str
    baseline_asr: float
    hardened_asr: float
    asr_delta: float  # baseline_asr - hardened_asr (positive means defense improved security)
    baseline_grade: RiskGrade
    hardened_grade: RiskGrade
    resolved_scenarios: list[str] = Field(default_factory=list)
    persistent_scenarios: list[str] = Field(default_factory=list)
    category_deltas: dict[str, float] = Field(default_factory=dict)
