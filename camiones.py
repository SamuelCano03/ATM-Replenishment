import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class CamionAgent(Agent):
    class StatusBehaviour(CyclicBehaviour):
        def __init__(self, agent):
            super().__init__()
            self.agent = agent  # Guardamos el agente como un atributo

        async def run(self):
            # Ahora podemos acceder al agente directamente, porque lo pasamos como parámetro
            print(f"Soy el camión {self.agent.jid}, reportando mi estado.")
            
            # Enviar mensaje al coordinador
            msg = Message(to="saelcc03@localhost", body="Estado: disponible")
            await self.send(msg)
            await spade.asyncio.sleep(5)

    async def setup(self):
        print(f"Agente {self.jid} inicializado")
        # Pasamos el agente actual al comportamiento
        b = self.StatusBehaviour(self)  # Pasa el agente al comportamiento
        self.add_behaviour(b)

class CoordinadorAgent(Agent):
    class ReceiveBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # Espera mensajes
            if msg:
                print(f"Mensaje recibido de {msg.sender}: {msg.body}")

    async def setup(self):
        print(f"Coordinador {self.jid} inicializado")
        b = self.ReceiveBehaviour()
        self.add_behaviour(b)

async def main():
    camion = CamionAgent("ismaelkno@localhost", "isma")
    coordinador = CoordinadorAgent("saelcc03@localhost", "12345")

    await camion.start()
    await coordinador.start()

if __name__ == "__main__":
    spade.run(main())
