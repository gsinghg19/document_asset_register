import { useState } from "react";
import { uploadAsset } from "./api.js";

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10);
}

export default function UploadForm({ onUploaded }) {
  const [uploaderName, setUploaderName] = useState("");
  const [fileName, setFileName] = useState("");
  const [uploadDate, setUploadDate] = useState(todayIsoDate());
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState({ state: "idle" });

  function handleFileChange(event) {
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
    // Default the file name/description to the picked file's name, but only
    // if the user hasn't already typed something of their own.
    if (selected && !fileName) {
      setFileName(selected.name);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!file) {
      setStatus({ state: "error", message: "Please choose a file to upload." });
      return;
    }

    setStatus({ state: "uploading" });
    try {
      const entry = await uploadAsset({ uploaderName, fileName, uploadDate, file });
      setStatus({ state: "success", message: `Uploaded "${entry.fileName}".` });
      setUploaderName("");
      setFileName("");
      setUploadDate(todayIsoDate());
      setFile(null);
      event.target.reset();
      onUploaded?.(entry);
    } catch (err) {
      setStatus({ state: "error", message: err.message });
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="field">
        <label htmlFor="uploaderName">Uploader name</label>
        <input
          id="uploaderName"
          type="text"
          required
          value={uploaderName}
          onChange={(e) => setUploaderName(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="fileName">File name</label>
        <input
          id="fileName"
          type="text"
          required
          value={fileName}
          onChange={(e) => setFileName(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="uploadDate">Upload date</label>
        <input
          id="uploadDate"
          type="date"
          required
          value={uploadDate}
          onChange={(e) => setUploadDate(e.target.value)}
        />
      </div>

      <div className="field">
        <label htmlFor="file">Document</label>
        <input id="file" type="file" required onChange={handleFileChange} />
      </div>

      <button type="submit" disabled={status.state === "uploading"}>
        Upload
      </button>

      {status.state === "success" && <p className="status success">{status.message}</p>}
      {status.state === "error" && <p className="status error">{status.message}</p>}
    </form>
  );
}
