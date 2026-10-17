import asyncio
import logging
from typing import Any, Dict, List


from agentverse.agents.base import BaseAgent
from agentverse.environments.rules.base import Rule
from agentverse.message import Message
from pydantic import Field

from . import env_registry as EnvironmentRegistry
from .base import BaseEnvironment


@EnvironmentRegistry.register("basic")
class BasicEnvironment(BaseEnvironment):
    """
    A basic environment implementing the logic of conversation.

    Args:
        agents: List of agents
        rule: Rule for the environment
        max_turns: Maximum number of turns
        cnt_turn: Current turn number
        last_messages: Messages from last turn
        rule_params: Variables set by the rule
    """

    agents: List[BaseAgent]
    rule: Rule
    max_turns: int = 10
    cnt_turn: int = 0
    last_messages: List[Message] = Field(default_factory=list)
    rule_params: Dict = {}

    def __init__(self, rule, **kwargs):
        rule_config = rule
        order_config = rule_config.get("order", {"type": "concurrent"})
        visibility_config = rule_config.get("visibility", {"type": "all"})
        selector_config = rule_config.get("selector", {"type": "basic"})
        updater_config = rule_config.get("updater", {"type": "basic"})
        describer_config = rule_config.get("describer", {"type": "basic"})
        rule = Rule(
            order_config,
            visibility_config,
            selector_config,
            updater_config,
            describer_config,
        )
        super().__init__(rule=rule, **kwargs)

    async def step(self) -> List[Message]:
        """Run one step of the environment"""


        agent_ids = self.rule.get_next_agent_idx(self)


        env_descriptions = self.rule.get_env_description(self)


        messages = await asyncio.gather(
            *[self.agents[i].astep(self, env_descriptions[i]) for i in agent_ids]
        )


        selected_messages = self.rule.select_message(self, messages)
        self.last_messages = selected_messages


        self.add_to_chat_history(selected_messages)


        self.rule.update_visible_agents(self)


        self.rule.update_memory(self)

        self.cnt_turn += 1

        return selected_messages

    def reset(self) -> None:
        """Reset the environment"""
        self.cnt_turn = 0
        self.last_messages = []
        self.complete_chat_history = []
        self.rule.reset()
        for agent in self.agents:
            agent.reset()

    def is_done(self) -> bool:
        """Check if the environment is done"""
        return self.cnt_turn >= self.max_turns
