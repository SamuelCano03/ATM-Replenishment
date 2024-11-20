document.getElementById("start-simulation").addEventListener("click", () => {
    fetch("/start", { method: "POST" })
        .then((response) => response.json())
        .then((data) => {
            alert(data.message);
        })
        .catch((error) => {
            console.error("Error al iniciar la simulación:", error);
        });
});

setInterval(() => {
    fetch("/status")
        .then((response) => response.json())
        .then((data) => {
            document.getElementById("simulation-status").innerText = `Status: ${data.status}`;
            document.getElementById("current-day").innerText = `Día actual: ${data.day}`;
            document.getElementById("routes").innerHTML = data.routes.map((r) => `<li>${r}</li>`).join("");
            document.getElementById("cashiers").innerHTML = data.cashiers.map((c) => `<li>${c}</li>`).join("");
        });
}, 1000);

