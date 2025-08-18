import pytest
from src.raspberry_friend.model.robot import Robot
from src.raspberry_friend.model.skill import NullSkill
from src.raspberry_friend.model.command import Command, CommandResult

def test_robot_dispatch_returns_nullskill_when_no_skills():
    """
    Test that Robot dispatch returns a CommandResult from NullSkill
    when no skills are registered to handle the command.
    """
    # Arrange
    robot = Robot()  # Robot without any skills
    command = Command(name="echo", args={"text": "Hello"})

    # Act
    result = robot.dispatch(command)

    # Assert
    assert isinstance(result, CommandResult)
    assert result.success is False
    assert "No skill" in result.message