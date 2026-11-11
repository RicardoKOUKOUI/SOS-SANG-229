import { useEffect, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { getProgress } from "../../api/actions.js";
import { useAuth } from "../../auth/AuthContext.jsx";

export default function ActionProgress({ onToast }) {
  const { actionId } = useOutletContext();
  const { token } = useAuth();
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    getProgress(token, actionId)
      .then(setProgress)
      .catch((err) => onToast?.(err.message || "Progression indisponible."));
  }, [token, actionId, onToast]);

  if (!progress) return <p className="text-accent">Chargement…</p>;

  return (
    <div>
      <p className="mb-4 text-sm font-semibold uppercase tracking-[0.18em] text-primary">
        ACT-008
      </p>
      <div className="card space-y-3">
        <p className="text-4xl font-extrabold text-primary">{progress.progress_percent}%</p>
        <p className="text-sm text-accent">
          Calculé depuis les tâches : {progress.task_done} done / {progress.task_total} total
          (doing {progress.task_doing}, todo {progress.task_todo}).
        </p>
        <div className="h-3 overflow-hidden rounded-full bg-light">
          <div
            className="h-full bg-primary transition-all"
            style={{ width: `${progress.progress_percent}%` }}
          />
        </div>
      </div>
    </div>
  );
}
