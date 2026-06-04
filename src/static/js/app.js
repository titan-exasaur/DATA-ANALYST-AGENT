const form = document.getElementById("analysisForm");
const statusCard = document.getElementById("statusCard");
const statusList = document.getElementById("statusList");
const reportCard = document.getElementById("reportCard");
const reportOutput = document.getElementById("reportOutput");
const chartsCard = document.getElementById("chartsCard");
const chartsOutput = document.getElementById("chartsOutput");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    statusCard.classList.remove("hidden");
    reportCard.classList.add("hidden");
    chartsCard.classList.add("hidden");

    statusList.innerHTML = "";
    reportOutput.textContent = "";
    chartsOutput.innerHTML = "";

    const submitButton = form.querySelector("button");
    submitButton.disabled = true;
    submitButton.textContent = "Running Analysis...";

    const formData = new FormData(form);

    try {
        const response = await fetch("/analyse", {
            method: "POST",
            body: formData
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        let buffer = "";

        while (true) {
            const { value, done } = await reader.read();

            if (done) {
                break;
            }

            buffer += decoder.decode(value, { stream: true });

            const events = buffer.split("\n\n");
            buffer = events.pop();

            for (const eventText of events) {
                if (!eventText.startsWith("data: ")) {
                    continue;
                }

                const jsonText = eventText.replace("data: ", "");
                const data = JSON.parse(jsonText);

                if (data.type === "status") {
                    addStatus(data.message);
                }

                if (data.type === "done") {
                    handleDone(data);
                }
            }
        }
    } catch (error) {
        addStatus("Frontend error: " + error.message);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Run Analysis";
    }
});

function addStatus(message) {
    const item = document.createElement("li");
    item.textContent = message;
    statusList.appendChild(item);
}

function handleDone(data) {
    if (!data.success) {
        reportCard.classList.remove("hidden");
        reportOutput.textContent = "Errors:\n" + data.errors.join("\n");
        return;
    }

    reportCard.classList.remove("hidden");
    reportOutput.textContent = data.report;

    if (data.charts && data.charts.length > 0) {
        chartsCard.classList.remove("hidden");

        data.charts.forEach(chart => {
            const wrapper = document.createElement("div");
            wrapper.className = "chart-box";
            wrapper.innerHTML = chart.html;
            chartsOutput.appendChild(wrapper);
        });
    }
}