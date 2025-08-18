async function fetchLogs() {
  try {
    const res = await fetch("http://localhost:5000/logs/");
    const logs = await res.json();
    renderLogsTable(logs);
  } catch (err) {
    console.error("Error fetching logs:", err);
    document.getElementById("logs-container").innerText =
      "Failed to load logs.";
  }
}

function renderLogsTable(logs) {
  const container = document.getElementById("logs-container");
  container.innerHTML = "";

  if (!logs.length) {
    container.innerText = "No logs found.";
    return;
  }

  const table = document.createElement("table");
  table.innerHTML = `
    <thead>
      <tr>
        <th>Time</th>
        <th>Source</th>
        <th>Destination</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody>
      ${logs
        .map(
          (l) => `<tr>
        <td>${l.time}</td>
        <td>${l.source}</td>
        <td>${l.destination}</td>
        <td>${l.action}</td>
      </tr>`
        )
        .join("")}
    </tbody>
  `;
  container.appendChild(table);
}
