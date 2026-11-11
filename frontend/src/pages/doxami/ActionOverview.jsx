import { useOutletContext } from "react-router-dom";

export default function ActionOverview() {
  const { project } = useOutletContext();
  if (!project) return null;
  return (
    <div className="card space-y-2">
      <p className="text-sm text-accent">
        Utilisez Kanban / Tasks pour avancer. La progression se recalcule depuis les statuts
        réels (todo / doing / done) — jamais simulée.
      </p>
      <p className="font-semibold">
        Progression actuelle : {project.progress_percent}%
      </p>
    </div>
  );
}
