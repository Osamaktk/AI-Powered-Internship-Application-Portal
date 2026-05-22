import { useMemo, useState } from "react";
import PersonalInfoSection from "./components/PersonalInfoSection";
import TrackSelectionSection from "./components/TrackSelectionSection";
import DocumentUploadSection from "./components/DocumentUploadSection";
import SubmitSection from "./components/SubmitSection";
import SpsProgramInfoSection from "./components/SpsProgramInfoSection";
import useFormSubmit from "./hooks/useFormSubmit";

const MAX_PHOTO_SIZE = 2 * 1024 * 1024;

const initialFields = {
  internship_year: "2026",
  first_name: "",
  last_name: "",
  email: "",
  phone: "",
  location: "PK",
  city: "",
  university: "",
  university_other: "",
  degree: "",
  major: "",
  cgpa: "",
  semester: "",
  class_ranking: "",
  class_ranking_other: "",
  field: "",
  selected_tracks: [],
  video_link: "",
};

const initialFiles = {
  cv: null,
  transcript: null,
  photo: null,
};

const initialVerificationState = {
  cvSlot: { status: "idle", filename: "", reason: "", evidence: [] },
  transcriptSlot: { status: "idle", filename: "", reason: "", evidence: [] },
};

export default function App() {
  const [fields, setFields] = useState(initialFields);
  const [files, setFiles] = useState(initialFiles);
  const [verificationState, setVerificationState] = useState(initialVerificationState);
  const [localError, setLocalError] = useState("");
  const { loading, result, error, submit, clearFeedback } = useFormSubmit();

  const selectedTracks = fields.selected_tracks;
  const canSubmit =
    verificationState.cvSlot.status === "verified" &&
    verificationState.transcriptSlot.status === "verified" &&
    !loading;

  const combinedError = useMemo(() => localError || error, [error, localError]);

  const setField = (key, value) => {
    clearFeedback();
    setLocalError("");
    setFields((previous) => ({ ...previous, [key]: value }));
  };

  const toggleTrack = (trackName) => {
    clearFeedback();
    setLocalError("");
    setFields((previous) => {
      return {
        ...previous,
        selected_tracks: [trackName],
      };
    });
  };

  const setPhoto = (file) => {
    clearFeedback();
    setLocalError("");

    if (!file) {
      setFiles((previous) => ({ ...previous, photo: null }));
      return;
    }

    const allowed = [".jpg", ".jpeg", ".png", ".gif"];
    const lower = file.name.toLowerCase();
    if (!allowed.some((ext) => lower.endsWith(ext))) {
      setLocalError("Photo must be JPG, JPEG, PNG, or GIF.");
      return;
    }
    if (file.size > MAX_PHOTO_SIZE) {
      setLocalError("Photo exceeds 2MB.");
      return;
    }

    setFiles((previous) => ({ ...previous, photo: file }));
  };

  const onSlotStateChange = (slotKey, nextState) => {
    clearFeedback();
    setLocalError("");
    setVerificationState((previous) => ({
      ...previous,
      [slotKey]: {
        ...previous[slotKey],
        ...nextState,
      },
    }));
  };

  const onVerifiedFileChange = (slotKey, file) => {
    clearFeedback();
    setLocalError("");
    const fileKey = slotKey === "cvSlot" ? "cv" : "transcript";
    setFiles((previous) => ({ ...previous, [fileKey]: file }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLocalError("");
    clearFeedback();

    if (!canSubmit) {
      setLocalError("Please upload and verify both documents to continue.");
      return;
    }
    if (selectedTracks.length < 1) {
      setLocalError("Please select one internship program.");
      return;
    }
    if (selectedTracks.length > 1) {
      setLocalError("Please select only one internship program.");
      return;
    }

    const universityValue =
      fields.university === "Other" ? fields.university_other.trim() : fields.university;
    if (!universityValue) {
      setLocalError("Please provide your university.");
      return;
    }

    const classRankingValue =
      fields.class_ranking === "Others"
        ? fields.class_ranking_other.trim()
        : fields.class_ranking;

    const submitFields = {
      ...fields,
      university: universityValue,
      class_ranking: classRankingValue,
      current_semester: fields.semester,
      selected_tracks: selectedTracks,
    };

    await submit({ fields: submitFields, files });
  };

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
      <header className="mb-6 rounded-2xl bg-brand-ink p-6 text-white shadow-panel sm:mb-8 sm:p-8">
        <p className="text-sm uppercase tracking-[0.2em] text-brand-mint">
          SPS SpinnLabs Internship to Job Program
        </p>
        <h1 className="mt-2 font-display text-3xl font-bold sm:text-4xl">
          SPS - Software Productivity Strategists Internship Application Portal
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-100 sm:text-base">
          Start your professional journey by joining the SPS Internship Program. Submit your
          profile, choose your internship program, and upload your documents for AI-based screening.
        </p>
        <a
          href="https://www.spsnet.com/spinnlabs_practice/internship-to-job-program/howitworks.php"
          target="_blank"
          rel="noreferrer"
          className="mt-4 inline-block rounded-lg border border-brand-mint px-3 py-2 text-sm font-semibold text-brand-mint transition hover:bg-brand-mint/10"
        >
          View Official SPS Program Details
        </a>
      </header>

      <div className="mb-6 sm:mb-8">
        <SpsProgramInfoSection />
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="animate-fade-slide">
          <PersonalInfoSection fields={fields} onFieldChange={setField} />
        </div>
        <div className="animate-fade-slide [animation-delay:120ms]">
          <TrackSelectionSection selectedTracks={selectedTracks} onToggleTrack={toggleTrack} />
        </div>
        <div className="animate-fade-slide [animation-delay:220ms]">
          <DocumentUploadSection
            videoLink={fields.video_link}
            onVideoLinkChange={(value) => setField("video_link", value)}
            photoFile={files.photo}
            onPhotoChange={setPhoto}
            verificationState={verificationState}
            onSlotStateChange={onSlotStateChange}
            onVerifiedFileChange={onVerifiedFileChange}
          />
        </div>
        <div className="animate-fade-slide [animation-delay:320ms]">
          <SubmitSection loading={loading} result={result} error={combinedError} canSubmit={canSubmit} />
        </div>
      </form>
    </main>
  );
}
