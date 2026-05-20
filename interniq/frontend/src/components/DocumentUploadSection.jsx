function FileUploadCard({
  label,
  accept,
  hint,
  required = false,
  fileName,
  onFileChange,
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
      <label className="mb-2 block text-sm font-semibold text-brand-ink">{label}</label>
      <input
        type="file"
        accept={accept}
        required={required}
        className="block w-full cursor-pointer rounded-lg border border-dashed border-slate-300 bg-white p-3 text-sm"
        onChange={(event) => onFileChange(event.target.files?.[0] || null)}
      />
      <p className="mt-2 text-xs text-slate-500">{hint}</p>
      <p className="mt-2 text-sm font-medium text-brand-cyan">
        {fileName ? `Selected: ${fileName}` : "No file selected"}
      </p>
    </div>
  );
}

export default function DocumentUploadSection({ fields, files, onFieldChange, onFileChange }) {
  return (
    <section className="panel">
      <h2 className="font-display text-2xl font-bold text-brand-ink">Section 3 — Documents</h2>
      <p className="mt-1 text-sm text-slate-600">
        Upload required files. Resume and transcript are mandatory.
      </p>

      <div className="mt-6 space-y-4">
        <div>
          <label className="mb-2 block text-sm font-semibold text-brand-ink">Video Interview Link</label>
          <input
            type="url"
            placeholder="https://..."
            className="w-full rounded-lg border border-slate-300 px-3 py-2"
            value={fields.video_link}
            onChange={(event) => onFieldChange("video_link", event.target.value)}
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <FileUploadCard
            label="Resume Upload (PDF)*"
            accept=".pdf,application/pdf"
            hint="PDF only, max 5MB."
            required
            fileName={files.resume?.name}
            onFileChange={(file) => onFileChange("resume", file)}
          />
          <FileUploadCard
            label="Transcript / Degree Upload (PDF)*"
            accept=".pdf,application/pdf"
            hint="PDF only, max 5MB."
            required
            fileName={files.transcript?.name}
            onFileChange={(file) => onFileChange("transcript", file)}
          />
        </div>

        <FileUploadCard
          label="Profile Photo"
          accept=".jpg,.jpeg,.png,.gif,image/jpeg,image/png,image/gif"
          hint="JPG/PNG/GIF only, max 2MB."
          fileName={files.photo?.name}
          onFileChange={(file) => onFileChange("photo", file)}
        />
      </div>
    </section>
  );
}
