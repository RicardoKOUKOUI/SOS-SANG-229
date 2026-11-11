import { useCallback, useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { getProject, listTasks, updateTask } from "../../api/actions.js";
import { useAuth } from "../../auth/AuthContext.jsx";

const COLUMNS = [
  { key: "todo", label: "À faire" },
  { key: "doing", label: "En cours" },
  { key: "done", label: "Fait" },
];

export default function ActionBoard({ onToast }) {
  const { actionId, setProject } = useOutletContext();
  const { token } = useAuth();
  const [tasks, setTasks] = useState([]);

  const reload = useCallback(async () => {
    const [taskData, projectData] = await Promise.all([
      listTasks(token, actionId),
      getProject(token, actionId),
    ]);
    setTasks(taskData);
    setProject?.(projectData);
  }, [token, actionId, setProject]);

  useEffect(() => {
    reload().catch((err) => onToast?.(err.message || "Kanban indisponible."));
  }, [reload, onToast]);

  async function move(task, status) {
    try {
      await updateTask(token, actionId, task.id, { status });
      await reload();
    } catch (err) {
      onToast?.(err.message || "Mise à jour impossible.");
    }
  }

  return (
    <div>
      <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-primary">
        ACT-005
      </p>
      <div className="grid gap-3 md:grid-cols-3">
        {COLUMNS.map((column) => (
          <div key={column.key} className="rounded-xl border border-light bg-paper p-3">
            <h3 className="font-bold">{column.label}</h3>
            <ul className="mt-3 space-y-2">
              {tasks
                .filter((task) => task.status === column.key)
                .map((task) => (
                  <li key={task.id} className="rounded-lg border border-light bg-white p-3">
                    <p className="text-sm font-semibold">{task.title}</p>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {COLUMNS.filter((item) => item.key !== task.status).map((item) => (
                        <button
                          key={item.key}
                          type="button"
                          className="rounded bg-light px-2 py-0.5 text-xs font-semibold"
                          onClick={() => move(task, item.key)}
                        >
                          → {item.label}
                        </button>
                      ))}
                    </div>
                  </li>
                ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
