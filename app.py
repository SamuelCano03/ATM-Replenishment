import asyncio
from flask import Flask, jsonify, request, render_template
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
import random
import math
from threading import Thread

app = Flask(__name__)
PWD = "12345"
NDIAS = 10

simulation_state = {
    "cajeros": [],
    "camion": None,
    "dias_transcurridos": 0,
    "costo_total": 0,
    "abastecimiento_total": 0,
    "status": "stopped",
}

class CajeroAgent(Agent):
    def __init__(self, jid, passwd, position):
        super().__init__(jid, passwd)
        self.position = position
        self.capacity = 100
        self.min_coef = 0.2
        self.monto = random.randint(int(self.min_coef * self.capacity), self.capacity)
        self.demanda = random.randint(self.monto, self.capacity)
        self.estado = "NO ABASTECIDO"

    def actualizar_necesidad(self):
        self.demanda = random.randint(0, self.capacity)
        self.estado = "NO ABASTECIDO"


class CamionAgent(Agent):
    def __init__(self, jid, passwd, cajeros):
        super().__init__(jid, passwd)
        self.position = (0, 0)
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

    async def run(self):
        cajeros = self.camion_agent.cajeros
        cajeros_necesitados = []

        for cajero in cajeros:
            cajero.actualizar_necesidad()
            if cajero.demanda > 0.5 * cajero.capacity:
                cajeros_necesitados.append(cajero)

        while cajeros_necesitados:
            c = min(
                cajeros_necesitados,
                key=lambda c: self.calcular_distancia(self.camion_agent.position, c.position),
            )
            self.camion_agent.costo_total += self.calcular_distancia(self.camion_agent.position, c.position)
            self.camion_agent.abastecimiento_total += c.demanda
            c.estado = "ABASTECIDO"
            cajeros_necesitados.remove(c)
            self.camion_agent.position = c.position

        simulation_state["dias_transcurridos"] = self.camion_agent.dia_actual
        simulation_state["costo_total"] = self.camion_agent.costo_total
        simulation_state["abastecimiento_total"] = self.camion_agent.abastecimiento_total
        simulation_state["camion"]["position"] = self.camion_agent.position
        simulation_state["cajeros"] = [
            {"jid": c.jid, "position": c.position, "estado": c.estado} for c in self.camion_agent.cajeros
        ]

        self.camion_agent.dia_actual += 1

        if self.camion_agent.dia_actual <= NDIAS:
            await asyncio.sleep(1)

        if self.camion_agent.dia_actual > NDIAS:
            simulation_state["status"] = "stopped" 
            self.kill()
            return

    def calcular_distancia(self, pos1, pos2):
        return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)



def run_simulation_async(cajeros, camion):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run_simulation():
        await asyncio.gather(*(agent.start() for agent in cajeros))
        await camion.start()

        await asyncio.sleep(NDIAS + 1)

        for cajero in cajeros:
            await cajero.stop()
        await camion.stop()

        simulation_state["status"] = "stopped"
        simulation_state["dias_transcurridos"] = NDIAS

    loop.run_until_complete(run_simulation())


@app.route("/")
def index():
    return render_template("index.html", simulation_state=simulation_state)


@app.route("/start", methods=["POST"])
def start_simulation():
    global simulation_state

    data = request.get_json()
    cajeros_data = data.get("cajeros", [])
    cajeros = [CajeroAgent(f"cajero{i+1}@localhost", PWD, tuple(c["position"])) for i, c in enumerate(cajeros_data)]
    camion = CamionAgent("camion@localhost", PWD, cajeros)

    simulation_state["cajeros"] = [
        {"jid": c.jid, "position": c.position, "estado": c.estado} for c in cajeros
    ]
    simulation_state["camion"] = {"jid": camion.jid, "position": camion.position}
    simulation_state["dias_transcurridos"] = 0
    simulation_state["costo_total"] = 0
    simulation_state["abastecimiento_total"] = 0
    simulation_state["status"] = "running"

    simulation_thread = Thread(target=run_simulation_async, args=(cajeros, camion))
    simulation_thread.start()

    return jsonify({"message": "Simulación iniciada", "cajeros": simulation_state["cajeros"]})


@app.route("/status", methods=["GET"])
def get_status():
    return jsonify(simulation_state)


@app.route("/stop", methods=["POST"])
def stop_simulation():
    simulation_state["dias_transcurridos"] = NDIAS 
    simulation_state["status"] = "stopped"
    return jsonify({"message": "Simulación detenida"})


if __name__ == "__main__":
    app.run(debug=True)
