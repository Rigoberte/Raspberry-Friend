from src.domain.models.command import Command
from src.domain.models.workflows.workflow_step import WorkflowStep
from src.domain.models.workflows.workflow_task import WorkflowTask


def build_transcribe_me_workflow(command: Command) -> WorkflowTask:
    # Si el usuario pasa un número como primer token, úsalo como duración
    args = command.get_args() or {}
    text = str(args.get("text", "")).strip()
    duration = None
    if text:
        first = text.split()[0]
        try:
            maybe = float(first)
            if maybe > 0:
                duration = maybe
        except ValueError:
            pass

    record_text = str(duration) if duration is not None else ""

    steps = [
        WorkflowStep(
            name="record",
            command=lambda ctx: Command("record-audio", {"text": record_text}),
            on_success=lambda ctx, res: ctx.update(res.get_data()),
        ),
        WorkflowStep(
            name="transcribe",
            command=lambda ctx: Command("transcribe", {"text": ctx.get("path", "")}),
            on_success=lambda ctx, res: ctx.update(res.get_data()),
        ),
    ]

    return WorkflowTask(steps, initial_context={})
