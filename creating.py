import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour


class AgentExample(Agent):
    async def setup(self):
        print(f"{self.jid} created.")


class CreateBehav(OneShotBehaviour):
    async def run(self):
        agent2 = AgentExample("saelcc03@localhost", "12345")
        await agent2.start()

async def main():
    agent1 = AgentExample("ismaelkno@localhost", "isma")
    behav = CreateBehav()
    agent1.add_behaviour(behav)
    await agent1.start()

    # wait until the behaviour is finished to quit spade.
    await behav.join()

if __name__ == "__main__":
    spade.run(main())
