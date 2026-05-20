import { useMemo, useState } from "react";
import { TRACK_GROUPS } from "../data/formOptions";

const groupLabels = {
  projects: "Projects",
  competencies: "Competencies",
  specializations: "Specializations",
};

function TrackCheckbox({ name, isSelected, disabled, onToggle }) {
  return (
    <label
      className={`flex cursor-pointer items-center justify-between rounded-lg border px-3 py-2 transition ${
        isSelected ? "border-brand-cyan bg-cyan-50" : "border-slate-200 bg-white"
      } ${disabled ? "cursor-not-allowed opacity-55" : "hover:border-brand-cyan"}`}
    >
      <span className="text-sm font-medium text-slate-700">{name}</span>
      <input
        type="checkbox"
        checked={isSelected}
        onChange={() => onToggle(name)}
        disabled={disabled}
      />
    </label>
  );
}

export default function TrackSelectionSection({ selectedTracks, onToggleTrack }) {
  const [openGroups, setOpenGroups] = useState({
    projects: true,
    competencies: true,
    specializations: true,
  });

  const selectedCount = selectedTracks.length;
  const selectedSet = useMemo(() => new Set(selectedTracks), [selectedTracks]);

  const toggleCollapse = (groupName) => {
    setOpenGroups((previous) => ({
      ...previous,
      [groupName]: !previous[groupName],
    }));
  };

  return (
    <section className="panel">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="font-display text-2xl font-bold text-brand-ink">Section 2 — Track Selection</h2>
          <p className="mt-1 text-sm text-slate-600">
            Select at least one and up to three tracks across all sections.
          </p>
        </div>
        <div className="rounded-full bg-brand-ink px-4 py-2 text-center text-sm font-semibold text-white">
          {selectedCount} / 3 selected
        </div>
      </div>

      <div className="mt-5 space-y-3">
        {Object.entries(TRACK_GROUPS).map(([groupName, tracks]) => (
          <div key={groupName} className="rounded-xl border border-slate-200 bg-slate-50/60">
            <button
              type="button"
              onClick={() => toggleCollapse(groupName)}
              className="flex w-full items-center justify-between px-4 py-3 text-left"
            >
              <span className="font-display text-lg font-semibold text-brand-ink">
                {groupLabels[groupName]}
              </span>
              <span className="text-sm font-semibold text-slate-500">
                {openGroups[groupName] ? "Collapse" : "Expand"}
              </span>
            </button>

            {openGroups[groupName] && (
              <div className="grid gap-3 px-4 pb-4">
                {tracks.map((track) => {
                  const isSelected = selectedSet.has(track);
                  const disabled = !isSelected && selectedCount >= 3;
                  return (
                    <TrackCheckbox
                      key={track}
                      name={track}
                      isSelected={isSelected}
                      disabled={disabled}
                      onToggle={onToggleTrack}
                    />
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
