const button = document.getElementById("health-button");
const result = document.getElementById("result");

button.addEventListener("click", async () => {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    result.textContent = JSON.stringify(await response.json(), null, 2);
  } catch (error) {
    result.textContent = `Error: ${error.message}`;
  }
});
