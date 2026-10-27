const form = document.getElementById("todo-form");
const titleInput = document.getElementById("todo-title");
const list = document.getElementById("todo-list");
const empty = document.getElementById("empty");
const result = document.getElementById("result");

async function request(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

async function loadTodos() {
  const todos = await request("/api/todos");
  list.replaceChildren();
  empty.textContent = todos.length === 0 ? "No to-dos yet." : "";
  for (const todo of todos) {
    const item = document.createElement("li");
    item.classList.toggle("complete", todo.is_complete);
    const title = document.createElement("span");
    title.className = "todo-title";
    title.textContent = todo.title;
    const complete = document.createElement("button");
    complete.type = "button";
    complete.textContent = todo.is_complete ? "Completed" : "Complete";
    complete.disabled = todo.is_complete;
    complete.setAttribute("aria-label", `Complete ${todo.title}`);
    complete.addEventListener("click", () => changeTodo(
      complete, `/api/todos/${todo.id}/complete`, "PATCH"
    ));
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "Delete";
    remove.setAttribute("aria-label", `Delete ${todo.title}`);
    remove.addEventListener("click", () => changeTodo(
      remove, `/api/todos/${todo.id}`, "DELETE"
    ));
    item.append(title, complete, remove);
    list.append(item);
  }
}

async function changeTodo(button, path, method) {
  result.textContent = "";
  button.disabled = true;
  try {
    await request(path, { method });
    await loadTodos();
  } catch (error) {
    result.textContent = `Error: ${error.message}`;
  } finally {
    button.disabled = false;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (!title) {
    result.textContent = "Enter a to-do title.";
    titleInput.focus();
    return;
  }
  result.textContent = "";
  const button = form.querySelector("button");
  button.disabled = true;
  try {
    await request("/api/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    form.reset();
    await loadTodos();
    titleInput.focus();
  } catch (error) {
    result.textContent = `Error: ${error.message}`;
  } finally {
    button.disabled = false;
  }
});

loadTodos().catch((error) => {
  empty.textContent = "";
  result.textContent = `Error: ${error.message}`;
});
