import random
import math
import spade
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

PWD = "12345"
NDIAS = 2

class CajeroAgent(Agent):
    def __init__(self, jid, passwd, position):
        super().__init__(jid, passwd)
        self.position = position
        self.capacity = 100
        self.min_coef = 0.2
        self.monto = random.randint(int(self.min_coef*self.capacity),self.capacity)
        self.prev = 0
        self.estado = "NO ABASTECIDO"
        self.demanda = random.randint(self.monto,self.capacity)

    async def setup(self):
        print(f"{self.jid} está en la posición {self.position} y necesita abastecimiento de {self.demanda}%")
        
    def actualizar_necesidad(self):
        self.estado = "NO ABASTECIDO"
        self.demanda = random.randint(0,int(0.8*self.capacity))

class CamionAgent(Agent):
    def __init__(self, jid, passwd, cajeros):
        super().__init__(jid, passwd)
        self.position = (0, 0)  # El camión empieza en (0,0)
        self.costo_total = 0
        self.abastecimiento_total = 0
        self.dia_actual = 1 
        self.cajeros = cajeros
        
    async def setup(self):
        self.add_behaviour(AbastecerCajerosBehaviour(self))

class AbastecerCajerosBehaviour(CyclicBehaviour):
    def __init__(self, camion_agent):
        super().__init__()
        self.camion_agent = camion_agent
        self.cajeros = camion_agent.cajeros
    
    async def run(self):
        print(f"\n\nDía {self.camion_agent.dia_actual} - El camión inicia su recorrido.")

        cajeros = self.cajeros
        cajeros_necesitados = []
        cajeros_no_necesitados = []
        for cajero in cajeros:
            cajero.actualizar_necesidad()
            print(f"{cajero.jid} reporta una demanda de {cajero.demanda}.")
            if cajero.demanda > 0.5 * cajero.capacity or cajero.monto < cajero.demanda:
                cajeros_necesitados.append(cajero)
            else:
                cajeros_no_necesitados.append(cajero)

        for cajero in cajeros_no_necesitados:
            cajero.prev = cajero.monto
            cajero.monto -= cajero.demanda

        while cajeros_necesitados:
            c = min(cajeros_necesitados, key=lambda c: self.calcular_distancia(self.camion_agent.position, c.position))
            
            print(f"El camión en {self.camion_agent.position} se dirige a {c.jid} en {c.position}. Necesita {c.demanda}. Monto actual: {c.monto}")
            abastecimiento = random.randint(int(c.min_coef*c.capacity) + c.demanda-c.monto, c.capacity)
            c.prev = c.monto
            c.monto += abastecimiento - c.demanda
            c.estado = "ABASTECIDO"
            self.camion_agent.costo_total += self.calcular_distancia(self.camion_agent.position, c.position)
            self.camion_agent.abastecimiento_total += abastecimiento
            self.camion_agent.position = c.position
            cajeros_necesitados.remove(c)

        self.camion_agent.dia_actual += 1

        print("\nReporte del día {self.camion_agent.dia_actual}:")
        for cajero in cajeros:
            print(f"CAJERO: {cajero.jid} DEMANDA: {cajero.demanda}. MONTO PREVIO: {cajero.prev}. MONTO ACTUAL: {cajero.monto}. ABASTECIDO: {cajero.monto - cajero.prev + cajero.demanda}. ESTADO: {cajero.estado}")

        if self.camion_agent.dia_actual > NDIAS:
            print(f"\nSimulación terminada. El camión ha abastecido por {NDIAS} días.")
            print(f"\nCosto total de transporte: {self.camion_agent.costo_total}")
            print(f"Total de abastecimiento: {self.camion_agent.abastecimiento_total}")
            self.kill()
            return

    def calcular_distancia(self, pos1, pos2):
        return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)


async def main():
    cajeros = [
        CajeroAgent("cajero1@localhost", PWD, (5, 5)),
        CajeroAgent("cajero2@localhost", PWD, (2, 8)),
        CajeroAgent("cajero3@localhost", PWD, (7, 1)),
    ]
    camion = CamionAgent("camion@localhost", PWD, cajeros)
    await camion.start()

if __name__ == "__main__":
    spade.run(main())

