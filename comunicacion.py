import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class SenderAgent(Agent):
    class SendBehav(CyclicBehaviour):
        async def run(self):
            msg = Message(to="ismaelkno@localhost")  # Dirección del receptor
            msg.body = "Hola, receptor!"  # Mensaje de texto
            print("Enviando mensaje: ", msg.body)
            await self.send(msg)
            await asyncio.sleep(2)  # Pausa entre envíos

    async def setup(self):
        print("SenderAgent iniciando...")
        b = self.SendBehav()
        self.add_behaviour(b)


class ReceiverAgent(Agent):
    class ReceiveBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)  # Espera un mensaje (5 seg)
            if msg:
                print("Mensaje recibido: ", msg.body)
            else:
                print("No se recibió mensaje.")

    async def setup(self):
        print("ReceiverAgent iniciando...")
        b = self.ReceiveBehav()
        self.add_behaviour(b)


async def main():
    sender = SenderAgent("saelcc03@localhost", "12345")
    receiver = ReceiverAgent("ismaelkno@localhost", "isma")

    await sender.start()
    await receiver.start()

    print("Agentes en ejecución. Ctrl+C para detener.")
    await asyncio.sleep(10)  # Deja que los agentes funcionen un rato

    await sender.stop()
    await receiver.stop()

if __name__ == "__main__":
    asyncio.run(main())

