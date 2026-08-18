const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function uploadAsset({ uploaderName, fileName, uploadDate, file }) {
  const formData = new FormData();
  formData.append("uploaderName", uploaderName);
  formData.append("fileName", fileName);
  formData.append("uploadDate", uploadDate);
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/assets`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail || `Upload failed (${response.status})`);
  }

  return response.json();
}

export async function listAssets() {
  const response = await fetch(`${API_BASE_URL}/assets`);
  if (!response.ok) {
    throw new Error(`Failed to load assets (${response.status})`);
  }
  return response.json();
}
