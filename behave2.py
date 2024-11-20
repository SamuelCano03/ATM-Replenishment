import asyncio
import spade
from spade import wait_until_finished
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import signal

class DummyAgent(Agent):
    class MyBehav(CyclicBehaviour):
        async def on_start(self):
            print("Starting behaviour . . .")
            self.counter = 0

        async def run(self):
            print(f"Counter: {self.counter}")
            self.counter += 1
            await asyncio.sleep(1)

    async def setup(self):
        print("Agent starting . . .")
        b = self.MyBehav()
        self.add_behaviour(b)

async def main():
    dummy = DummyAgent("saelcc03@localhost", "12345")
    await dummy.start()
    await wait_until_finished(dummy)

# Manejar la señal SIGINT para cerrar el agente correctamente
def signal_handler(sig, frame):
    print("\nCtrl+C received, shutting down...")
    loop.stop()

if __name__ == "__main__":
    # Registra el manejador de señales
    spade.run(main())
    loop = asyncio.get_event_loop()
    signal.signal(signal.SIGINT, signal_handler)  # Captura Ctrl+C
    
    # Corre la aplicación

