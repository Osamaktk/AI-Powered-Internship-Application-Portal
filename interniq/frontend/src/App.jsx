import { useMemo, useState } from "react";
import PersonalInfoSection from "./components/PersonalInfoSection";
import TrackSelectionSection from "./components/TrackSelectionSection";
import DocumentUploadSection from "./components/DocumentUploadSection";
import SubmitSection from "./components/SubmitSection";
import useFormSubmit from "./hooks/useFormSubmit";

const MAX_PDF_SIZE = 5 * 1024 * 1024;
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
  resume: null,
  transcript: null,
  photo: null,
};

export default function App() {
  const [fields, setFields] = useState(initialFields);
  const [files, setFiles] = useState(initialFiles);
  const [localError, setLocalError] = useState("");
  const { loading, result, error, submit, clearFeedback } = useFormSubmit();

  const selectedTracks = fields.selected_tracks;

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
      const alreadySelected = previous.selected_tracks.includes(trackName);
      if (alreadySelected) {
        return {
          ...previous,
          selected_tracks: previous.selected_tracks.filter((track) => track !== trackName),
        };
      }
      if (previous.selected_tracks.length >= 3) {
        return previous;
      }
      return {
        ...previous,
        selected_tracks: [...previous.selected_tracks, trackName],
      };
    });
  };

  const setFile = (fileKey, file) => {
    clearFeedback();
    setLocalError("");
    if (!file) {
      setFiles((previous) => ({ ...previous, [fileKey]: null }));
      return;
    }

    const isPdfKey = fileKey === "resume" || fileKey === "transcript";
    if (isPdfKey) {
      if (!file.name.toLowerCase().endsWith(".pdf")) {
        setLocalError(`${fileKey === "resume" ? "Resume" : "Transcript"} must be a PDF.`);
        return;
      }
      if (file.size > MAX_PDF_SIZE) {
        setLocalError(`${fileKey === "resume" ? "Resume" : "Transcript"} exceeds 5MB.`);
        return;
      }
    } else if (fileKey === "photo") {
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
    }

    setFiles((previous) => ({ ...previous, [fileKey]: file }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLocalError("");
    clearFeedback();

    if (selectedTracks.length < 1) {
      setLocalError("Please select at least one track.");
      return;
    }
    if (selectedTracks.length > 3) {
      setLocalError("You can select up to 3 tracks only.");
      return;
    }
    if (!files.resume || !files.transcript) {
      setLocalError("Resume and transcript files are required.");
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
      selected_tracks: selectedTracks,
    };

    await submit({ fields: submitFields, files });
  };

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
      <header className="mb-6 rounded-2xl bg-brand-ink p-6 text-white shadow-panel sm:mb-8 sm:p-8">
        <p className="text-sm uppercase tracking-[0.2em] text-brand-mint">SPS Internship Portal</p>
        <h1 className="mt-2 font-display text-3xl font-bold sm:text-4xl">InternIQ Application Form</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-100 sm:text-base">
          Submit your profile, choose your preferred tracks, and upload your documents for AI-based
          screening.
        </p>
      </header>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="animate-fade-slide">
          <PersonalInfoSection fields={fields} onFieldChange={setField} />
        </div>
        <div className="animate-fade-slide [animation-delay:120ms]">
          <TrackSelectionSection selectedTracks={selectedTracks} onToggleTrack={toggleTrack} />
        </div>
        <div className="animate-fade-slide [animation-delay:220ms]">
          <DocumentUploadSection
            fields={fields}
            files={files}
            onFieldChange={setField}
            onFileChange={setFile}
          />
        </div>
        <div className="animate-fade-slide [animation-delay:320ms]">
          <SubmitSection loading={loading} result={result} error={combinedError} />
        </div>
      </form>
    </main>
  );
}
