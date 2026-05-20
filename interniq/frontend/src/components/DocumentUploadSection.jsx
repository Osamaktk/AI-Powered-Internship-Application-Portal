import { useRef, useState } from "react";
import { verifyDocumentFile } from "../api/client";
import VerificationModal from "./VerificationModal";

function Spinner() {
  return (
    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-blue-500 border-r-transparent" />
  );
}

function StatusStrip({ slot }) {
  const status = slot?.status || "idle";

  if (status === "checking") {
    return (
      <div className="mt-3 flex items-center gap-2 rounded-lg bg-blue-50 px-3 py-2 text-sm text-blue-700">
        <Spinner />
        <span>Analyzing document with AI…</span>
      </div>
    );
  }

  if (status === "verified") {
    return (
      <div className="mt-3 rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
        ✅ {slot.filename} — Verified
      </div>
    );
  }

  if (status === "rejected") {
    return (
      <div className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
        ❌ {slot.filename || "Document"} — Incorrect document
      </div>
    );
  }

  return (
    <div className="mt-3 rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-600">
      📄 No file selected
    </div>
  );
}

function UploadSlot({
  title,
  helperText,
  slot,
  inputRef,
  onSelectFile,
  onDropFile,
}) {
  const isChecking = slot?.status === "checking";

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
      <p className="mb-2 text-sm font-semibold text-brand-ink">{title}</p>
      <label
        className={`block rounded-lg border border-dashed bg-white p-4 text-sm ${
          isChecking ? "cursor-not-allowed opacity-60" : "cursor-pointer hover:border-brand-cyan"
        }`}
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          if (isChecking) {
            return;
          }
          const file = event.dataTransfer.files?.[0] || null;
          onDropFile(file);
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          disabled={isChecking}
          className="hidden"
          onChange={(event) => onSelectFile(event.target.files?.[0] || null)}
        />
        <span className="font-medium text-slate-700">
          {isChecking ? "Analyzing document…" : "Upload PDF or drag and drop"}
        </span>
        <p className="mt-1 text-xs text-slate-500">{helperText}</p>
      </label>
      <StatusStrip slot={slot} />
      {slot?.status === "rejected" && slot?.reason && (
        <p className="mt-2 text-sm text-red-700">{slot.reason}</p>
      )}
    </div>
  );
}

export default function DocumentUploadSection({
  videoLink,
  onVideoLinkChange,
  photoFile,
  onPhotoChange,
  verificationState,
  onSlotStateChange,
  onVerifiedFileChange,
}) {
  const cvInputRef = useRef(null);
  const transcriptInputRef = useRef(null);
  const [modalState, setModalState] = useState({
    open: false,
    documentLabel: "",
    reason: "",
    evidence: [],
  });

  const setRejectedModal = (documentLabel, reason, evidence) => {
    setModalState({
      open: true,
      documentLabel,
      reason,
      evidence: evidence || [],
    });
  };

  const closeModal = () => {
    setModalState((previous) => ({ ...previous, open: false }));
  };

  const verifyFile = async (slotKey, documentLabel, expectedType, file, inputRef) => {
    if (!file) {
      onSlotStateChange(slotKey, {
        status: "idle",
        filename: "",
        reason: "",
        evidence: [],
      });
      onVerifiedFileChange(slotKey, null);
      return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      const reason = "Only PDF files are allowed.";
      onSlotStateChange(slotKey, {
        status: "rejected",
        filename: file.name,
        reason,
        evidence: [],
      });
      onVerifiedFileChange(slotKey, null);
      if (inputRef?.current) {
        inputRef.current.value = "";
      }
      setRejectedModal(documentLabel, reason, []);
      return;
    }

    onSlotStateChange(slotKey, {
      status: "checking",
      filename: file.name,
      reason: "",
      evidence: [],
    });

    const response = await verifyDocumentFile(file, expectedType);
    const reason = response?.reason || "Document verification failed.";
    const evidence = Array.isArray(response?.evidence) ? response.evidence : [];

    if (response?.verified) {
      onSlotStateChange(slotKey, {
        status: "verified",
        filename: file.name,
        reason: "",
        evidence: [],
      });
      onVerifiedFileChange(slotKey, file);
      return;
    }

    onSlotStateChange(slotKey, {
      status: "rejected",
      filename: file.name,
      reason,
      evidence,
    });
    onVerifiedFileChange(slotKey, null);
    if (inputRef?.current) {
      inputRef.current.value = "";
    }
    setRejectedModal(documentLabel, reason, evidence);
  };

  return (
    <section className="panel">
      <h2 className="font-display text-2xl font-bold text-brand-ink">Section 3 — Documents</h2>
      <p className="mt-1 text-sm text-slate-600">
        Upload and verify both required documents before submitting.
      </p>

      <div className="mt-6 space-y-4">
        <div>
          <label className="mb-2 block text-sm font-semibold text-brand-ink">Video Interview Link</label>
          <input
            type="url"
            placeholder="https://..."
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={videoLink}
            onChange={(event) => onVideoLinkChange(event.target.value)}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <UploadSlot
            title="CV Upload (PDF)*"
            helperText="Expected document type: CV / Resume."
            slot={verificationState.cvSlot}
            inputRef={cvInputRef}
            onSelectFile={(file) => verifyFile("cvSlot", "CV", "cv", file, cvInputRef)}
            onDropFile={(file) => verifyFile("cvSlot", "CV", "cv", file, cvInputRef)}
          />
          <UploadSlot
            title="Transcript Upload (PDF)*"
            helperText="Expected document type: Academic transcript."
            slot={verificationState.transcriptSlot}
            inputRef={transcriptInputRef}
            onSelectFile={(file) =>
              verifyFile("transcriptSlot", "Transcript", "transcript", file, transcriptInputRef)
            }
            onDropFile={(file) =>
              verifyFile("transcriptSlot", "Transcript", "transcript", file, transcriptInputRef)
            }
          />
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
          <label className="mb-2 block text-sm font-semibold text-brand-ink">Profile Photo</label>
          <input
            type="file"
            accept=".jpg,.jpeg,.png,.gif,image/jpeg,image/png,image/gif"
            className="block w-full cursor-pointer rounded-lg border border-dashed border-slate-300 bg-white p-3 text-sm"
            onChange={(event) => onPhotoChange(event.target.files?.[0] || null)}
          />
          <p className="mt-2 text-xs text-slate-500">Optional. JPG/PNG/GIF, max 2MB.</p>
          <p className="mt-2 text-sm font-medium text-brand-cyan">
            {photoFile ? `Selected: ${photoFile.name}` : "No photo selected"}
          </p>
        </div>
      </div>

      <VerificationModal
        open={modalState.open}
        documentLabel={modalState.documentLabel}
        reason={modalState.reason}
        evidence={modalState.evidence}
        onClose={closeModal}
      />
    </section>
  );
}
