"""
Unit tests for SkillRegistry.
"""

import pytest
from src.application.services.skill_registry import SkillRegistry
from src.domain.models.command import Command, CommandResult


class MockSkill:
    """Mock skill for testing."""
    
    def handle(self, command: Command) -> CommandResult:
        return CommandResult(success=True, message="Mock skill executed")


class TestSkillRegistry:
    """Tests for SkillRegistry service."""

    def test_register_skill(self):
        """Test that a skill can be registered."""
        # Arrange
        registry = SkillRegistry()
        skill = MockSkill()

        # Act
        registry.register("mock", skill)
        retrieved = registry.get("mock")

        # Assert
        assert retrieved is skill

    def test_register_multiple_skills(self):
        """Test that multiple skills can be registered."""
        # Arrange
        registry = SkillRegistry()
        skill1 = MockSkill()
        skill2 = MockSkill()

        # Act
        registry.register("skill1", skill1)
        registry.register("skill2", skill2)

        # Assert
        assert registry.get("skill1") is skill1
        assert registry.get("skill2") is skill2

    def test_get_nonexistent_skill_returns_none(self):
        """Test that getting a non-existent skill returns None."""
        # Arrange
        registry = SkillRegistry()

        # Act
        result = registry.get("nonexistent")

        # Assert
        assert result is None

    def test_list_empty_registry(self):
        """Test that list() returns empty list for empty registry."""
        # Arrange
        registry = SkillRegistry()

        # Act
        skills = registry.list()

        # Assert
        assert skills == []

    def test_list_registered_skills(self):
        """Test that list() returns sorted list of registered skill names."""
        # Arrange
        registry = SkillRegistry()
        registry.register("echo", MockSkill())
        registry.register("time", MockSkill())
        registry.register("weather", MockSkill())

        # Act
        skills = registry.list()

        # Assert
        assert skills == ["echo", "time", "weather"]

    def test_register_overwrites_existing_skill(self):
        """Test that registering a skill with same name overwrites the previous one."""
        # Arrange
        registry = SkillRegistry()
        skill1 = MockSkill()
        skill2 = MockSkill()

        # Act
        registry.register("mock", skill1)
        registry.register("mock", skill2)
        retrieved = registry.get("mock")

        # Assert
        assert retrieved is skill2
        assert retrieved is not skill1
