document.addEventListener("DOMContentLoaded", () => {
    const startSimulationButton = document.getElementById("start-simulation");
    const simulationStatus = document.getElementById("simulation-status");
    const currentDay = document.getElementById("current-day");
    const cashiersList = document.getElementById("cashiers");

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function updateGraph(cashiers, truckPosition) {
        console.log("Actualizando gráfico", cashiers, truckPosition);
    
        const svg = d3.select("#visualization svg");
    
        const cashiersSelection = svg.selectAll(".cashier")
            .data(cashiers, d => d.jid);
    
        cashiersSelection.enter()
            .append("circle")
            .attr("class", "cashier")
            .attr("cx", d => d.position[0] * 50)
            .attr("cy", d => d.position[1] * 50)
            .attr("r", 20)
            .attr("fill", d => d.estado === "ABASTECIDO" ? "lightblue" : "lightcoral")
            .attr("stroke", "white")
            .attr("stroke-width", 2)
            .merge(cashiersSelection) 
            .transition() 
            .duration(500)
            .attr("fill", d => d.estado === "ABASTECIDO" ? "lightblue" : "lightcoral")
    
        const textSelection = svg.selectAll(".cashierText")
            .data(cashiers, d => d.jid); 
    
        textSelection.enter()
            .append("text")
            .attr("class", "cashierText")
            .attr("x", d => d.position[0] * 50)
            .attr("y", d => d.position[1] * 50)
            .attr("dy", 6)  
            .attr("text-anchor", "middle")  
            .attr("fill", "white")  
            .attr("font-size", "18px")
            .text(d => {
                const jidString = String(d.jid);  
                const match = jidString.match(/(\d+)/);  
                return match ? match[0] : '';  
            })
            .merge(textSelection)
            .transition()
            .duration(500)
            .attr("x", d => d.position[0] * 50)
            .attr("y", d => d.position[1] * 50)
            .text(d => {
               
                const jidString = String(d.jid);  
                const match = jidString.match(/(\d+)/);  
                return match ? match[0] : '';  
            });
    

        cashiersSelection.exit().remove();
        textSelection.exit().remove();  

  
        const truckSelection = svg.selectAll(".truck")
            .data([truckPosition]);

        truckSelection.enter()
            .append("circle")
            .attr("class", "truck")
            .attr("cx", truckPosition[0] * 50)
            .attr("cy", truckPosition[1] * 50)
            .attr("r", 15) 
            .attr("fill", "green")
            .attr("stroke", "black")
            .attr("stroke-width", 2)
            .merge(truckSelection)  
            .transition()
            .duration(500)
            .attr("cx", truckPosition[0] * 50)
            .attr("cy", truckPosition[1] * 50);
        
     
        truckSelection.exit().remove();
    }
    

    startSimulationButton.addEventListener("click", async () => {
    
        const minX = 1; 
        const minY = 1;
        const maxX = 12;
        const maxY = 10;
        const cantidadCajeros = 10;
    
  
        const posicionesGeneradas = []; 
    
 
        const cajerosAleatorios = Array.from({ length: cantidadCajeros }, () => {
            return { position: generarPosicionAleatoria(minX, minY, maxX, maxY, posicionesGeneradas) };
        });
    

        const response = await fetch("/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cajeros: cajerosAleatorios, 
            }),
        });
    
        const result = await response.json();
        console.log(result.message);
    

        let simulationRunning = true;
    
        while (simulationRunning) {
            const statusResponse = await fetch("/status");
            const statusData = await statusResponse.json();
    
 
            updateUI(statusData);
            updateGraph(statusData.cajeros, statusData.camion.position);
    
   
            if (statusData.status === "stopped") {
                simulationRunning = false;
                console.log("Simulación terminada, deteniendo actualizaciones.");
            }
    

            await sleep(1000);
        }
    
   
        await fetch("/stop", { method: "POST" });
    });
    

    function generarPosicionAleatoria(minX, minY, maxX, maxY, posicionesGeneradas) {
        let nuevaPosicion;
        let posicionValida = false;
    

        while (!posicionValida) {
            nuevaPosicion = [
                Math.floor(Math.random() * (maxX - minX)) + minX, 
                Math.floor(Math.random() * (maxY - minY)) + minY 
            ];
    

            if (!posicionesGeneradas.some(pos => pos[0] === nuevaPosicion[0] && pos[1] === nuevaPosicion[1])) {
                posicionesGeneradas.push(nuevaPosicion); 
                posicionValida = true; 
            }
        }
    
        return nuevaPosicion;
    }


    function updateCashiers(cashiers) {
        cashiersList.innerHTML = ""; 
        cashiers.forEach((cashier) => {
      
            const jid = Array.isArray(cashier.jid) ? cashier.jid[0] : cashier.jid;
    
          
            console.log("jid de cajero:", jid);
    
          
            let cashierId = (typeof jid === 'string' && jid.match(/\d+/)) 
                ? jid.match(/\d+/)[0] 
                : 'Desconocido';
            
          
            const formattedState = cashier.estado.charAt(0).toUpperCase() + cashier.estado.slice(1).toLowerCase();
    
         
            const listItem = document.createElement("li");
            listItem.textContent = `Cajero: ${cashierId}, Estado: ${formattedState}, Posición: (${cashier.position[0]}, ${cashier.position[1]})`;
            cashiersList.appendChild(listItem);
        });
    }
    
    

  
    function updateUI(statusData) {
        simulationStatus.textContent = `Estado: ${statusData.status}`;
        currentDay.textContent = `Día: ${statusData.dias_transcurridos}`; 
        updateCashiers(statusData.cajeros);
    }

});
