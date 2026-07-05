import React, { useEffect, useState } from "react";
import { uploadDocument, listDocuments, deleteDocument } from "../services/api.js";

export default function DocumentUploadPage() {
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  function refresh() {
    listDocuments()
      .then(setDocuments)
      .catch(() => setError("Unable to load documents. Please log in again."));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleUpload(e) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await uploadDocument(file);
      setFile(null);
      refresh();
    } catch (err) {
      setError("Upload failed. Please check the file type and try again.");
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this document from the knowledge base?")) return;
    await deleteDocument(id);
    refresh();
  }

  return (
    <div className="container">
      <h2>Knowledge Base Documents</h2>

      <div className="card">
        <h3>Upload New Document</h3>
        <form onSubmit={handleUpload}>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => setFile(e.target.files[0])}
          />
          {error && <p className="error-text">{error}</p>}
          <button className="btn" type="submit" disabled={uploading || !file}>
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </form>
      </div>

      <div className="card">
        <h3>Existing Documents</h3>
        <table>
          <thead>
            <tr>
              <th>File Name</th>
              <th>Type</th>
              <th>Uploaded</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.document_id}>
                <td>{doc.file_name}</td>
                <td>{doc.file_type.toUpperCase()}</td>
                <td>{new Date(doc.upload_date).toLocaleString()}</td>
                <td>{doc.status}</td>
                <td>
                  <button className="btn btn-danger" onClick={() => handleDelete(doc.document_id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
