import random
import math
import spade
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.behaviour import CyclicBehaviour

PWD = "12345"

class CajeroAgent(Agent):
    def __init__(self, jid,passwd, position):
        super().__init__(jid,passwd)
        self.position = position
        self.max_capacity = 100
        self.necesita_abastecimiento = random.randint(50, 100)  # Generar entre 50% y 100% de la capacidad

    async def setup(self):
        print(f"{self.jid} está en la posición {self.position} y necesita abastecimiento de {self.necesita_abastecimiento}%")
        
class CamionAgent(Agent):
    def __init__(self, jid,passwd):
        super().__init__(jid,passwd)
        self.position = (0, 0)  # El camión empieza en (0,0)
        self.costo_total = 0
    
    async def setup(self):
        self.add_behaviour(AbastecerCajerosBehaviour(self))

class AbastecerCajerosBehaviour(CyclicBehaviour):
    def __init__(self, camion_agent):
        super().__init__()
        self.camion_agent = camion_agent
    
    async def run(self):
        cajeros = self.get_all_cajeros()
        # Filtro: solo cajeros que necesitan más del 80% de su capacidad
        cajeros_necesitados = [cajero for cajero in cajeros if cajero.necesita_abastecimiento > 0.7 * cajero.max_capacity]

        while cajeros_necesitados:
            cajero = min(cajeros_necesitados, key=lambda c: self.calcular_distancia(self.camion_agent.position, c.position))
            
            print(f"El camión ubicado en {self.camion_agent.position} se dirige a {cajero.jid} en la posición {cajero.position}. Necesita {cajero.necesita_abastecimiento}")
            costo_transporte = self.calcular_distancia(self.camion_agent.position, cajero.position)
            self.camion_agent.costo_total += costo_transporte
            self.camion_agent.position = cajero.position
            
            cajero.necesita_abastecimiento = 0  # cambiar
            
            cajeros_necesitados.remove(cajero)
    
    def calcular_distancia(self, pos1, pos2):
        return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)

    def get_all_cajeros(self):
        cajeros = [
            CajeroAgent("cajero1@localhost",PWD, (5, 5)),
            CajeroAgent("cajero2@localhost",PWD, (2, 8)),
            CajeroAgent("cajero3@localhost",PWD, (7, 1))
        ]
        return cajeros

async def main():
    camion = CamionAgent("camion@localhost",PWD)
    await camion.start()

if __name__ == "__main__":
    spade.run(main())


