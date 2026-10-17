import asyncio

from agentverse.initialization import load_agent, load_environment, prepare_task_config


class AgentVerse:
    def __init__(self, agents, environment):
        self.agents = agents
        self.environment = environment

    @classmethod
    def from_config(cls, config, stage):
        task = prepare_task_config(config, stage)
        agents = [load_agent(agent) for agent in task["agents"]]
        environment = load_environment({**task["environment"], "agents": agents})
        return cls(agents, environment)

    async def arun(self):
        self.environment.reset()
        while not self.environment.is_done():
            await self.environment.step()

    def run(self):
        asyncio.run(self.arun())

    def reset(self):
        self.environment.reset()
