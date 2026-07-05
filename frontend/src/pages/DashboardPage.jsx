import React, { useEffect, useState } from "react";
import { getDashboardSummary } from "../services/api.js";

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getDashboardSummary()
      .then(setSummary)
      .catch(() => setError("Unable to load dashboard. Please log in again."));
  }, []);

  if (error) return <div className="container"><p className="error-text">{error}</p></div>;
  if (!summary) return <div className="container">Loading dashboard...</div>;

  return (
    <div className="container">
      <h2>Administrator Dashboard</h2>
      <div className="stat-grid">
        <div className="stat-box">
          <div className="value">{summary.total_documents}</div>
          <div>Uploaded Documents</div>
        </div>
        <div className="stat-box">
          <div className="value">{summary.total_conversations}</div>
          <div>Conversations</div>
        </div>
        <div className="stat-box">
          <div className="value">{summary.total_sessions}</div>
          <div>Chat Sessions</div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Recently Uploaded Documents</h3>
        <table>
          <thead>
            <tr>
              <th>File Name</th>
              <th>Type</th>
              <th>Chunks</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {summary.recent_documents.map((doc) => (
              <tr key={doc.document_id}>
                <td>{doc.file_name}</td>
                <td>{doc.file_type.toUpperCase()}</td>
                <td>{doc.chunk_count}</td>
                <td>{doc.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
