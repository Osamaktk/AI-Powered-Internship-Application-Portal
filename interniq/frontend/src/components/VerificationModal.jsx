import { useEffect } from "react";

export default function VerificationModal({
  open,
  documentLabel,
  reason,
  evidence,
  onClose,
}) {
  useEffect(() => {
    if (!open) {
      return undefined;
    }
    const onKeyDown = (event) => {
      if (event.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === "Escape") {
          onClose();
        }
      }}
    >
      <div
        className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <h3 className="font-display text-xl font-bold text-brand-ink">
          Incorrect Document Detected
        </h3>
        <p className="mt-3 text-sm text-slate-700">
          The file you uploaded does not appear to be a valid {documentLabel}.
        </p>
        <p className="mt-3 text-sm text-slate-700">
          <span className="font-semibold">Reason:</span> {reason}
        </p>

        <div className="mt-4 text-sm text-slate-700">
          <p className="font-semibold">Evidence found:</p>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            {(evidence || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
            {(!evidence || evidence.length === 0) && <li>No specific evidence provided.</li>}
          </ul>
        </div>

        <p className="mt-4 text-sm text-slate-700">
          Please upload the correct document and try again.
        </p>

        <button
          type="button"
          onClick={onClose}
          className="mt-6 rounded-lg bg-brand-ink px-4 py-2 text-sm font-semibold text-white"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}
