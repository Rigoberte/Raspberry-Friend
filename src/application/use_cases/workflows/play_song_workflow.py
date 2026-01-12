from src.domain.models.command import Command
from src.domain.models.workflows.workflow_step import WorkflowStep
from src.domain.models.workflows.workflow_task import WorkflowTask

def build_play_song_workflow(command: Command) -> WorkflowTask:
    song_name = command.get_args().get("text", "")
    
    steps = [
        WorkflowStep(
            name="find-song",
            command=lambda ctx: Command("find-song", {"text": song_name}),
            on_success=lambda ctx, res: ctx.update(res.get_data())  # guarda path en ctx
        ),
        WorkflowStep(
            name="play-mp3",
            command=lambda ctx: Command("play-mp3", {"path": ctx["path"]})
        ),
    ]
    return WorkflowTask(steps, initial_context={"song_name": song_name})