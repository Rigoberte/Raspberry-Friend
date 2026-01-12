from __future__ import annotations
from typing import Callable

from src.domain.models.command import Command
from src.domain.models.task import Task
from src.domain.models.tasks.immediate_task import ImmediateTask
from src.domain.models.tasks.scheduled_task import ScheduledTask
from src.domain.models.tasks.recurring_task import RecurringTask
from src.domain.models.tasks.continuous_task import ContinuousTask
from src.domain.models.scheduling_policy import ScheduleKind
from src.application.services.scheduling_policy_parser import SchedulingPolicyParser

from src.application.use_cases.workflows.play_song_workflow import build_play_song_workflow #TODO: replace to do it extensible


class CommandToTask:
    def __init__(self, policy_parser: SchedulingPolicyParser) -> None:
        self._policy_parser = policy_parser
        
        self._workflow_builders: dict[str, Callable[[Command], Task]] = {
            "play-song": build_play_song_workflow,
        }

    def build(self, command: Command) -> Task:
        name = command.get_name()
        args = command.get_args() or {}
        text = str(args.get("text", "")).strip()

        if name in self._workflow_builders:
            builder = self._workflow_builders[name]
            return builder(command)

        policy = self._policy_parser.parse(text)

        if policy.kind == ScheduleKind.IMMEDIATE:
            return ImmediateTask(command)

        if policy.kind == ScheduleKind.AT and policy.at is not None:
            return ScheduledTask(command, policy.at)

        if policy.kind == ScheduleKind.EVERY and policy.interval is not None:
            return RecurringTask(command, check_interval=policy.interval, max_executions=policy.max_executions)

        if policy.kind == ScheduleKind.CONTINUOUS and policy.interval is not None:
            condition = policy.condition or (lambda: True)
            return ContinuousTask(command, check_interval=policy.interval, condition_checker=condition, max_executions=policy.max_executions)

        # Fallback
        return ImmediateTask(command)