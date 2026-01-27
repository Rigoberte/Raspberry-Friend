from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult
from src.domain.ports.outbound.ai_chatbot_ports import AI_ChatBotPort


class AI_ChatbotSkill(RobotSkill):
    """
    Skill que envía un prompt a Gemini y devuelve la respuesta textual.
    """

    def __init__(self, gemini_service: AI_ChatBotPort):
        super().__init__({"gemini": "Ejecuta un prompt en Gemini (google-genai)."})
        self._gemini = gemini_service

    def handle(self, command: Command) -> CommandResult:
        prompt = str(command.get_args().get("text", "")).strip()
        if not prompt:
            return CommandResult(
                success=False,
                message="Debes proporcionar un prompt. Ejemplo: 'gemini escribe una historia sobre robots'.",
            )

        result = self._gemini.generate_text(prompt)
        if not result.get("success", False):
            return CommandResult(
                success=False,
                message=str(result.get("message", "No se pudo obtener respuesta de Gemini")),
            )

        message = str(result.get("message", "Gemini no devolvió contenido.")).strip()
        return CommandResult(success=True, message=message)
