const form = document.getElementById("todo-form");
const titleInput = document.getElementById("todo-title");
const dueDateInput = document.getElementById("todo-due-date");
const list = document.getElementById("todo-list");
const empty = document.getElementById("empty");
const result = document.getElementById("result");
const viewButtons = document.querySelectorAll("[data-view]");
let selectedView = "all";
let pending = false;

async function request(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

async function loadTodos() {
  list.replaceChildren();
  empty.textContent = "Loading to-dos...";
  const path = selectedView === "overdue" ? "/api/todos?overdue=true" : "/api/todos";
  const todos = await request(path);
  empty.textContent = todos.length === 0
    ? (selectedView === "overdue" ? "No overdue to-dos." : "No to-dos yet.")
    : "";
  for (const todo of todos) {
    const item = document.createElement("li");
    item.classList.toggle("complete", todo.is_complete);
    const title = document.createElement("span");
    title.className = "todo-title";
    title.textContent = todo.title;
    const dateLabel = document.createElement("label");
    dateLabel.htmlFor = `due-date-${todo.id}`;
    dateLabel.textContent = "Due date";
    const dueDate = document.createElement("input");
    dueDate.id = dateLabel.htmlFor;
    dueDate.type = "date";
    dueDate.value = todo.due_date || "";
    dueDate.setAttribute("aria-label", `Due date for ${todo.title}`);
    const save = document.createElement("button");
    save.type = "button";
    save.textContent = "Save";
    save.setAttribute("aria-label", `Save due date for ${todo.title}`);
    save.addEventListener("click", () => {
      if (!dueDate.reportValidity()) {
        return;
      }
      return changeTodo(`/api/todos/${todo.id}/due-date`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ due_date: dueDate.value || null }),
      });
    });
    const complete = document.createElement("button");
    complete.type = "button";
    complete.textContent = todo.is_complete ? "Completed" : "Complete";
    complete.disabled = todo.is_complete;
    complete.setAttribute("aria-label", `Complete ${todo.title}`);
    complete.addEventListener("click", () => changeTodo(
      `/api/todos/${todo.id}/complete`, { method: "PATCH" }
    ));
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "Delete";
    remove.setAttribute("aria-label", `Delete ${todo.title}`);
    remove.addEventListener("click", () => changeTodo(
      `/api/todos/${todo.id}`, { method: "DELETE" }
    ));
    item.append(title, dateLabel, dueDate, save, complete, remove);
    list.append(item);
  }
}

async function runAction(action) {
  if (pending) {
    return;
  }
  pending = true;
  result.textContent = "";
  const controls = Array.from(document.querySelectorAll("button, input"),
    (control) => [control, control.disabled]);
  for (const [control] of controls) {
    control.disabled = true;
  }
  try {
    await action();
  } catch (error) {
    result.textContent = `Error: ${error.message}`;
    if (empty.textContent === "Loading to-dos...") {
      empty.textContent = "";
    }
  } finally {
    for (const [control, disabled] of controls) {
      control.disabled = disabled;
    }
    pending = false;
  }
}

async function changeTodo(path, options) {
  await runAction(async () => {
    await request(path, options);
    await loadTodos();
  });
}

for (const button of viewButtons) {
  button.addEventListener("click", () => runAction(async () => {
    selectedView = button.dataset.view;
    for (const viewButton of viewButtons) {
      viewButton.setAttribute("aria-pressed",
        String(viewButton.dataset.view === selectedView));
    }
    await loadTodos();
  }));
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = titleInput.value.trim();
  if (!title) {
    result.textContent = "Enter a to-do title.";
    titleInput.focus();
    return;
  }
  await runAction(async () => {
    await request("/api/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, due_date: dueDateInput.value || null }),
    });
    form.reset();
    await loadTodos();
  });
  titleInput.focus();
});

runAction(loadTodos);
