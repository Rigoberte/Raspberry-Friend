from src.application.use_cases.skills.skill import RobotSkill
from src.domain.models.command import Command, CommandResult


class CalculatorSkill(RobotSkill):
    def __init__(self):
        super().__init__({"calculate": "Evaluate a mathematical expression."})

    def handle(self, command: Command) -> CommandResult:
        try:
            expression = command.get_args().get("text", "")
            if not self.__is_a_valid_expression(expression):
                return CommandResult(False, "Invalid characters or unbalanced parentheses in expression.")
            
            result = eval(expression)
            return CommandResult(True, f"The result of '{expression}' is {result}.")
        except Exception:
            return CommandResult(False, "Invalid or missing 'expression' argument for calculate command.")    
            
    def __is_a_valid_expression(self, expression: str) -> bool:
        allowed_chars = "0123456789+-*/(). "
        
        expression = str(expression).replace(" ", "")

        if not all(char in allowed_chars for char in expression):
            return False

        amount_of_opening_parentheses = 0
        for char in expression:
            if char == "(":
                amount_of_opening_parentheses += 1
            elif char == ")":
                amount_of_opening_parentheses -= 1
                if amount_of_opening_parentheses < 0:
                    return False
        if amount_of_opening_parentheses != 0:
            return False
        
        # TODO: Check if the expression structure is valid (e.g., no consecutive operators)

        return True