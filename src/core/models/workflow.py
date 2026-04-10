"""长流程任务状态模型。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ActionDecision:
    action: str
    reason: str
    requires_confirm: bool = False


@dataclass(slots=True)
class TaskRuntimeState:
    is_running: bool = False
    is_paused: bool = False
    counters: dict[str, int] = field(default_factory=dict)
