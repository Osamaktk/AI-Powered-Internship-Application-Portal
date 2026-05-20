import { useState } from "react";
import { submitApplication } from "../api/client";

export default function useFormSubmit() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const clearFeedback = () => {
    setResult(null);
    setError("");
  };

  const submit = async ({ fields, files }) => {
    setLoading(true);
    clearFeedback();

    const payload = new FormData();
    Object.entries(fields).forEach(([key, value]) => {
      if (key === "selected_tracks") {
        payload.append(key, JSON.stringify(value || []));
        return;
      }
      payload.append(key, value ?? "");
    });

    payload.append("resume", files.resume);
    payload.append("transcript", files.transcript);
    if (files.photo) {
      payload.append("photo", files.photo);
    }

    try {
      const response = await submitApplication(payload);
      setResult(response);
      return response;
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Unexpected error while submitting.";
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    result,
    error,
    clearFeedback,
    submit,
  };
}
