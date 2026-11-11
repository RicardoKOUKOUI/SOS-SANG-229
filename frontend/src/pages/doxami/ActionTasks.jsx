import { useCallback, useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { createTask, getProject, listTasks, updateTask } from "../../api/actions.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function ActionTasks({ onToast }) {
  const { actionId, setProject } = useOutletContext();
  const { token } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState("");
  const [busy, setBusy] = useState(false);

  const reload = useCallback(async () => {
    const [taskData, projectData] = await Promise.all([
      listTasks(token, actionId),
      getProject(token, actionId),
    ]);
    setTasks(taskData);
    setProject?.(projectData);
  }, [token, actionId, setProject]);

  useEffect(() => {
    reload().catch((err) => onToast?.(err.message || "Tasks indisponibles."));
  }, [reload, onToast]);

  async function onAdd(event) {
    event.preventDefault();
    setBusy(true);
    try {
      await createTask(token, actionId, { title: title.trim() });
      setTitle("");
      await reload();
    } catch (err) {
      onToast?.(err.message || "Ajout impossible.");
    } finally {
      setBusy(false);
    }
  }

  async function cycle(task) {
    const next = task.status === "todo" ? "doing" : task.status === "doing" ? "done" : "todo";
    try {
      await updateTask(token, actionId, task.id, { status: next });
      await reload();
    } catch (err) {
      onToast?.(err.message || "Mise à jour impossible.");
    }
  }

  return (
    <div>
      <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-primary">
        ACT-006
      </p>
      <form className="flex gap-2" onSubmit={onAdd}>
        <input
          className="field-input flex-1"
          required
          placeholder="Nouvelle tâche"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <button className="btn-primary" type="submit" disabled={busy}>
          Ajouter
        </button>
      </form>
      <ul className="mt-4 space-y-2">
        {tasks.map((task) => (
          <li key={task.id} className="card flex items-center justify-between gap-3">
            <div>
              <p className="font-semibold">{task.title}</p>
              <p className="text-xs uppercase tracking-wide text-accent">{task.status}</p>
            </div>
            <button
              type="button"
              className="rounded-lg bg-light px-3 py-1 text-sm font-semibold"
              onClick={() => cycle(task)}
            >
              Avancer
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
