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
