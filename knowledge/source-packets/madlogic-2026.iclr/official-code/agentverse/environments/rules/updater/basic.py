from . import updater_registry
from .base import BaseUpdater


@updater_registry.register("basic")
class BasicUpdater(BaseUpdater):
    def update_memory(self, environment):
        for message in environment.last_messages:
            if message.content:
                for agent in environment.agents:
                    if "all" in message.receiver or agent.name in message.receiver:
                        agent.add_message_to_memory([message])
