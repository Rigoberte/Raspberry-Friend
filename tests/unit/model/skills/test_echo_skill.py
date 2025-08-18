import pytest
from src.raspberry_friend.model.robot import Robot
from src.raspberry_friend.model.command import Command, CommandResult
from src.raspberry_friend.model.skills.echo_skill import EchoSkill

def test_echo_skill_handles_command():
    """
    Test that EchoSkill correctly handles an 'echo' command.
    """
    # Arrange
    robot = Robot()
    echo_skill = EchoSkill()
    robot.register(echo_skill)
    command = Command(name="echo", args={"text": "Hello World"})

    # Act
    result = robot.dispatch(command)

    # Assert
    assert isinstance(result, CommandResult)
    assert result.success is True
    assert result.message == "Hello World"

def test_echo_skill_cannot_handle_other_command():
    """
    Test that EchoSkill does not handle unrelated commands.
    """
    # Arrange
    echo_skill = EchoSkill()
    command = Command(name="remind", args={})

    # Act
    can_handle = echo_skill.can_handle(command)

    # Assert
    assert can_handle is False