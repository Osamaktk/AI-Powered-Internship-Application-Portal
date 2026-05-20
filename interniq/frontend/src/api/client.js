const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function submitApplication(formData) {
  const response = await fetch(`${API_BASE_URL}/apply`, {
    method: "POST",
    body: formData,
  });

  let data;
  try {
    data = await response.json();
  } catch {
    data = { detail: "Invalid server response." };
  }

  if (!response.ok) {
    const message = data?.detail || "Submission failed.";
    throw new Error(message);
  }

  return data;
}

export async function verifyDocumentFile(file, expectedType) {
  const payload = new FormData();
  payload.append("file", file);
  payload.append("expected_type", expectedType);

  const response = await fetch(`${API_BASE_URL}/api/verify-document`, {
    method: "POST",
    body: payload,
  });

  let data;
  try {
    data = await response.json();
  } catch {
    data = {
      verified: false,
      confidence: "low",
      reason: "Invalid server response.",
      evidence: [],
    };
  }

  if (!response.ok) {
    return {
      verified: false,
      confidence: "low",
      reason: data?.detail || "Verification request failed.",
      evidence: [],
    };
  }

  return data;
}
