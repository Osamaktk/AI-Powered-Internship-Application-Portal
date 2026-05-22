export default function SubmitSection({ loading, result, error, canSubmit }) {
  const showReceived = ["received", "accepted"].includes(result?.status);
  const showRejected = result?.status === "rejected";
  const isDisabled = !canSubmit;

  return (
    <section className="panel">
      <h2 className="font-display text-2xl font-bold text-brand-ink">Section 4 - Submit</h2>
      <p className="mt-1 text-sm text-slate-600">
        Review everything, then submit your application.
      </p>

      <div className="mt-5">
        <button
          type="submit"
          disabled={isDisabled}
          title={isDisabled ? "Please upload and verify both documents to continue" : ""}
          className={`w-full rounded-xl px-4 py-3 font-display text-lg font-bold text-white transition ${
            isDisabled
              ? "cursor-not-allowed bg-slate-500 opacity-50"
              : "bg-brand-ink hover:bg-slate-900"
          }`}
        >
          {loading ? "Submitting..." : "APPLY"}
        </button>
      </div>

      {error && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {showReceived && (
        <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          <p className="font-semibold">Application received.</p>
          <p className="mt-1">
            {result?.message || "Your application has been received and we will be in touch very soon."}
          </p>
        </div>
      )}

      {showRejected && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <p className="font-semibold">Application rejected.</p>
          <p className="mt-1">{result?.reason || "Document verification failed."}</p>
        </div>
      )}
    </section>
  );
}

