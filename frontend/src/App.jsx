import { useEffect, useState } from "react";
import UploadForm from "./UploadForm.jsx";
import AssetList from "./AssetList.jsx";
import { listAssets } from "./api.js";

export default function App() {
  const [assets, setAssets] = useState([]);
  const [loadError, setLoadError] = useState(null);

  function refreshAssets() {
    listAssets()
      .then(setAssets)
      .catch((err) => setLoadError(err.message));
  }

  useEffect(refreshAssets, []);

  return (
    <main>
      <h1>Document Asset Register</h1>

      <section>
        <h2>Upload a document</h2>
        <UploadForm onUploaded={refreshAssets} />
      </section>

      <section>
        <h2>Uploaded documents</h2>
        {loadError && <p className="status error">{loadError}</p>}
        <AssetList assets={assets} />
      </section>
    </main>
  );
}
