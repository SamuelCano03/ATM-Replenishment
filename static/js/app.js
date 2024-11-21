document.addEventListener("DOMContentLoaded", () => {
    const startSimulationButton = document.getElementById("start-simulation");
    const simulationStatus = document.getElementById("simulation-status");
    const currentDay = document.getElementById("current-day");
    const cashiersList = document.getElementById("cashiers");

    // Función para simular una espera (pausa) de X segundos
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Función para actualizar los nodos (cajeros y camión)
    function updateGraph(cashiers, truckPosition) {
        console.log("Actualizando gráfico", cashiers, truckPosition);
    
        const svg = d3.select("#visualization svg");
    
        // Actualizamos los nodos de los cajeros
        const cashiersSelection = svg.selectAll(".cashier")
            .data(cashiers, d => d.jid);  // Usamos 'jid' para identificar cada cajero de forma única
    
        cashiersSelection.enter()
            .append("circle")
            .attr("class", "cashier")
            .attr("cx", d => d.position[0] * 50)
            .attr("cy", d => d.position[1] * 50)
            .attr("r", 20)
            .attr("fill", d => d.estado === "ABASTECIDO" ? "lightblue" : "lightcoral")
            .attr("stroke", "white")
            .attr("stroke-width", 2)
            .merge(cashiersSelection)  // Merge con los nodos existentes
            .transition()  // Agrega una transición para los cambios
            .duration(500)
            .attr("fill", d => d.estado === "ABASTECIDO" ? "lightblue" : "lightcoral")
    
        // Actualizamos el texto de los números de cajero
        const textSelection = svg.selectAll(".cashierText")
            .data(cashiers, d => d.jid);  // Usamos 'jid' para identificar de manera única cada cajero
    
        textSelection.enter()
            .append("text")
            .attr("class", "cashierText")
            .attr("x", d => d.position[0] * 50)
            .attr("y", d => d.position[1] * 50)
            .attr("dy", 6)  // Ajuste para que el texto esté en el centro del círculo
            .attr("text-anchor", "middle")  // Centrar el texto
            .attr("fill", "white")  // Color blanco para el texto
            .attr("font-size", "18px")  // Tamaño de la fuente
            .text(d => {
                // Asegurarse de que d.jid es una cadena de texto
                const jidString = String(d.jid);  // Convertir a cadena si no lo es
                const match = jidString.match(/(\d+)/);  // Busca solo los números en el jid
                return match ? match[0] : '';  // Si hay un número, lo devuelve; si no, un string vacío
            })
            .merge(textSelection)
            .transition()
            .duration(500)
            .attr("x", d => d.position[0] * 50)
            .attr("y", d => d.position[1] * 50)
            .text(d => {
                // Asegurarse de que d.jid es una cadena y extraer el número
                const jidString = String(d.jid);  // Convertir a cadena si no lo es
                const match = jidString.match(/(\d+)/);  // Busca solo los números en el jid
                return match ? match[0] : '';  // Si hay un número, lo devuelve; si no, un string vacío
            });
    
        // EXIT: Eliminar nodos que ya no están en los datos
        cashiersSelection.exit().remove();
        textSelection.exit().remove();  // Eliminar los textos si el cajero ya no está
    
        // Actualizamos el camión
        const truckSelection = svg.selectAll(".truck")
            .data([truckPosition]);  // El camión tiene una sola posición

        truckSelection.enter()
            .append("circle")
            .attr("class", "truck")
            .attr("cx", truckPosition[0] * 50)
            .attr("cy", truckPosition[1] * 50)
            .attr("r", 15)  // Tamaño del camión
            .attr("fill", "green")
            .attr("stroke", "black")
            .attr("stroke-width", 2)
            .merge(truckSelection)  // Merge con los nodos existentes
            .transition()
            .duration(500)
            .attr("cx", truckPosition[0] * 50)
            .attr("cy", truckPosition[1] * 50);
        
        // EXIT: Eliminar camión si ya no se encuentra en los datos
        truckSelection.exit().remove();
    }
    

    startSimulationButton.addEventListener("click", async () => {
        // Definir el mínimo y el máximo para las posiciones
        const minX = 1; // Mínimo valor en el eje X
        const minY = 1; // Mínimo valor en el eje Y
        const maxX = 12; // Máximo valor en el eje X (evitando que se salgan del canvas)
        const maxY = 10; // Máximo valor en el eje Y (evitando que se salgan del canvas)
        const cantidadCajeros = 10; // Número de cajeros
    
        // Array para almacenar las posiciones generadas y evitar duplicados
        const posicionesGeneradas = [];  // Asegúrate de que este array esté bien inicializado
    
        // Generar posiciones aleatorias para los cajeros dentro del rango sin repetir
        const cajerosAleatorios = Array.from({ length: cantidadCajeros }, () => {
            return { position: generarPosicionAleatoria(minX, minY, maxX, maxY, posicionesGeneradas) };
        });
    
        // Enviar la solicitud para iniciar la simulación
        const response = await fetch("/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cajeros: cajerosAleatorios,  // Usamos las posiciones aleatorias generadas
            }),
        });
    
        const result = await response.json();
        console.log(result.message);
    
        // Comenzar a hacer solicitudes a /status cada día
        let simulationRunning = true;
    
        while (simulationRunning) {
            const statusResponse = await fetch("/status");
            const statusData = await statusResponse.json();
    
            // Actualizar la interfaz de usuario
            updateUI(statusData);
            updateGraph(statusData.cajeros, statusData.camion.position);
    
            // Si la simulación está detenida, salimos del bucle
            if (statusData.status === "stopped") {
                simulationRunning = false;
                console.log("Simulación terminada, deteniendo actualizaciones.");
            }
    
            // Esperar 1 segundo antes de la siguiente actualización
            await sleep(1000);
        }
    
        // Llamar al endpoint /stop después de que la simulación haya alcanzado el último día
        await fetch("/stop", { method: "POST" });
    });
    
    // Función para generar una posición aleatoria dentro de un rango (minX, minY, maxX, maxY)
    function generarPosicionAleatoria(minX, minY, maxX, maxY, posicionesGeneradas) {
        let nuevaPosicion;
        let posicionValida = false;
    
        // Intentar generar una posición única
        while (!posicionValida) {
            nuevaPosicion = [
                Math.floor(Math.random() * (maxX - minX)) + minX,  // Posición aleatoria en el eje X
                Math.floor(Math.random() * (maxY - minY)) + minY   // Posición aleatoria en el eje Y
            ];
    
            // Comprobar si la nueva posición ya ha sido generada
            if (!posicionesGeneradas.some(pos => pos[0] === nuevaPosicion[0] && pos[1] === nuevaPosicion[1])) {
                posicionesGeneradas.push(nuevaPosicion);  // Guardar la nueva posición generada
                posicionValida = true;  // Posición válida, salir del bucle
            }
        }
    
        return nuevaPosicion;
    }

    // Función para actualizar la lista de cajeros
    function updateCashiers(cashiers) {
        cashiersList.innerHTML = ""; // Limpiar la lista
        cashiers.forEach((cashier) => {
            // Verificar si 'jid' es un array y extraer el primer elemento
            const jid = Array.isArray(cashier.jid) ? cashier.jid[0] : cashier.jid;
    
            // Verificar el valor de 'jid' antes de aplicar el regex
            console.log("jid de cajero:", jid);
    
            // Usar regex para extraer números del jid (si existe)
            let cashierId = (typeof jid === 'string' && jid.match(/\d+/)) 
                ? jid.match(/\d+/)[0] 
                : 'Desconocido';
            
            // Capitalizar la primera letra del estado
            const formattedState = cashier.estado.charAt(0).toUpperCase() + cashier.estado.slice(1).toLowerCase();
    
            // Crear el elemento de la lista
            const listItem = document.createElement("li");
            listItem.textContent = `Cajero: ${cashierId}, Estado: ${formattedState}, Posición: (${cashier.position[0]}, ${cashier.position[1]})`;
            cashiersList.appendChild(listItem);
        });
    }
    
    

    // Función para actualizar la interfaz de usuario
    function updateUI(statusData) {
        simulationStatus.textContent = `Estado: ${statusData.status}`; // Actualizar estado de la simulación
        currentDay.textContent = `Día: ${statusData.dias_transcurridos}`; // Actualizar el día actual
        updateCashiers(statusData.cajeros); // Actualizar la lista de cajeros
    }

});
