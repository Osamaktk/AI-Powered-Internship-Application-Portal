import { TRACK_GROUPS } from "../data/formOptions";

const ALL_INTERNSHIP_PROGRAMS = Object.values(TRACK_GROUPS).flat();

function ProgramOption({ programName, isSelected, onSelect }) {
  return (
    <label
      className={`flex cursor-pointer items-center justify-between rounded-lg border px-3 py-2 transition ${
        isSelected ? "border-brand-cyan bg-cyan-50" : "border-slate-200 bg-white hover:border-brand-cyan"
      }`}
    >
      <span className="text-sm font-medium text-slate-700">{programName}</span>
      <input
        type="radio"
        name="selected_program"
        checked={isSelected}
        onChange={() => onSelect(programName)}
      />
    </label>
  );
}

export default function TrackSelectionSection({ selectedTracks, onToggleTrack }) {
  const selectedProgram = selectedTracks[0] || "";
  const selectedCount = selectedProgram ? 1 : 0;

  return (
    <section className="panel">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="font-display text-2xl font-bold text-brand-ink">
            Section 2 - Internship Program Selection
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Select one internship program. Your application will be sent to that specific department head.
          </p>
        </div>
        <div className="rounded-full bg-brand-ink px-4 py-2 text-center text-sm font-semibold text-white">
          {selectedCount} / 1 selected
        </div>
      </div>

      <div className="mt-5 grid gap-3">
        {ALL_INTERNSHIP_PROGRAMS.map((programName) => (
          <ProgramOption
            key={programName}
            programName={programName}
            isSelected={selectedProgram === programName}
            onSelect={onToggleTrack}
          />
        ))}
      </div>
    </section>
  );
}

