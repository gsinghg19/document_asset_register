export default function AssetList({ assets }) {
  if (assets.length === 0) {
    return <p>No documents uploaded yet.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>File name</th>
          <th>Uploader</th>
          <th>Upload date</th>
        </tr>
      </thead>
      <tbody>
        {assets.map((asset) => (
          <tr key={asset.assetId}>
            <td>{asset.fileName}</td>
            <td>{asset.uploaderName}</td>
            <td>{asset.uploadDate}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
