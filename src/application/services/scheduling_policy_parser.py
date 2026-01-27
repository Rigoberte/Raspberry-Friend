from __future__ import annotations
from datetime import timedelta, datetime, timezone
from typing import Optional

from src.domain.models.scheduling_policy import SchedulingPolicy, ScheduleKind


class SchedulingPolicyParser:
    def parse(self, text: str) -> SchedulingPolicy:
        text = (text or "").strip()
        if not text:
            return SchedulingPolicy(kind=ScheduleKind.IMMEDIATE)

        try:
            if "-at:" in text:
                time_str = text.split("-at:", 1)[1].strip()
                at = self.__read_time__(time_str)
                return SchedulingPolicy(kind=ScheduleKind.AT, at=at)

            if "-every:" in text:
                interval_str = text.split("-every:", 1)[1].split("-max:")[0].split("-while:")[0].strip()
                unit = interval_str[-1]
                amount = int(interval_str[:-1]) if interval_str[:-1].isdigit() else 0

                if unit.lower() == "s":
                    interval = timedelta(seconds=amount)
                elif unit == "m":
                    interval = timedelta(minutes=amount)
                elif unit.lower() == "h":
                    interval = timedelta(hours=amount)
                elif unit.lower() == "d":
                    interval = timedelta(days=amount)
                elif unit.lower() == "w":
                    interval = timedelta(weeks=amount)
                elif unit == "M":
                    interval = timedelta(days=30 * amount)
                elif unit.lower() == "y":
                    interval = timedelta(days=365 * amount)
                else:
                    interval = timedelta(minutes=amount)

                max_executions: Optional[int] = None
                if "-max:" in text:
                    max_str = text.split("-max:", 1)[1].split("-while:")[0].strip()
                    if max_str.isdigit():
                        max_executions = int(max_str)

                if "-while:" in text:
                    condition_str = text.split("-while:", 1)[1].split("-max:")[0].split("-every:")[0].strip().lower()

                    def condition_checker() -> bool:
                        if condition_str in {"true", "1", "yes", "y", "si", "sí"}:
                            return True
                        if condition_str in {"false", "0", "no", "n"}:
                            return False
                        
                        return True

                    return SchedulingPolicy(
                        kind=ScheduleKind.CONTINUOUS,
                        interval=interval,
                        max_executions=max_executions,
                        condition=condition_checker,
                    )

                return SchedulingPolicy(
                    kind=ScheduleKind.EVERY,
                    interval=interval,
                    max_executions=max_executions,
                )

            return SchedulingPolicy(kind=ScheduleKind.IMMEDIATE)
        except Exception:
            
            return SchedulingPolicy(kind=ScheduleKind.IMMEDIATE)
        
    def __read_time__(self, time_str: str) -> datetime:
        now = datetime.now(timezone(timedelta(hours=-3)))

        # Día
        day_part = ""
        time_part = time_str
        if " " in time_str:
            day_part, time_part = time_str.split(" ", 1)
        if len(day_part) == 5 and day_part[2] == "-" and day_part[:2].isdigit() and day_part[3:].isdigit():
            day = int(day_part[:2])
            month = int(day_part[3:])
            scheduled_day = now.replace(day=day, month=month)
        else:
            scheduled_day = now

        # Hora
        h, m, s = 0, 0, 0
        if time_part.count(":") in (1, 2):
            parts = time_part.split(":")
            if all(p.isdigit() for p in parts):
                h = int(parts[0])
                m = int(parts[1]) if len(parts) > 1 else 0
                s = int(parts[2]) if len(parts) > 2 else 0

        scheduled_datetime = scheduled_day.replace(
            hour=h, minute=m, second=s, microsecond=0, tzinfo=timezone(timedelta(hours=-3))
        )

        if scheduled_datetime < now:
            scheduled_datetime += timedelta(days=1)

        return scheduled_datetime