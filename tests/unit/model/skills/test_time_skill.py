import pytest
from src.raspberry_friend.model.robot import Robot
from src.raspberry_friend.model.command import Command, CommandResult
from src.raspberry_friend.model.skills.time_skill import TimeSkill

def test_time_skill_handles_time_command():
    """
    Test that TimeSkill correctly handles a 'time' command.
    """
    # Arrange
    robot = Robot()
    time_skill = TimeSkill()
    robot.register(time_skill)
    command = Command(name="time", args={})

    # Act
    result = robot.dispatch(command)

    # Assert
    assert isinstance(result, CommandResult)
    assert result.success is True
    assert "Current time is" in result.message

def test_time_skill_cannot_handle_other_command():
    """
    Test that TimeSkill does not handle unrelated commands.
    """
    time_skill = TimeSkill()
    command = Command(name="echo", args={"text": "Hello"})

    can_handle = time_skill.can_handle(command)

    assert can_handle is False