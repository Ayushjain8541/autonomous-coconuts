"use strict";
const button = document.getElementById("load-demo");
const status = document.getElementById("status");
const result = document.getElementById("result");
button.addEventListener("click", async () => {
  button.disabled = true;
  status.textContent = "Loading fixture from the backend…";
  try {
    const response = await fetch("/api/demo");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error?.message || "Request failed");
    if (data.source?.mode !== "synthetic_demo") throw new Error("Unexpected bootstrap response mode");
    result.textContent = JSON.stringify(data, null, 2);
    status.textContent = `Loaded ${data.encounters.length} synthetic encounters. Fixture connectivity works; trained ML and live LLM remain unimplemented.`;
  } catch (error) {
    status.textContent = `Could not load demo: ${error.message}`;
    result.textContent = "No result available. Check the backend connection.";
  } finally {
    button.disabled = false;
  }
});
