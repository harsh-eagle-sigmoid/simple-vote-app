// frontend/src/App.jsx
import { useEffect, useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "";

function App() {
  const [question, setQuestion] = useState("");
  const [options, setOptions] = useState([]);
  const [totalVotes, setTotalVotes] = useState(0);
  const [loading, setLoading] = useState(true);
  const [voting, setVoting] = useState(false);
  const [error, setError] = useState("");

  const fetchVotes = async () => {
    try {
      setError("");
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/api/votes`);
      if (!res.ok) {
        throw new Error(`Failed to fetch votes: ${res.status}`);
      }
      const data = await res.json();
      setQuestion(data.question);
      setOptions(data.options);
      setTotalVotes(data.totalVotes);
    } catch (err) {
      console.error(err);
      setError("Failed to load votes. Check backend or network.");
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (optionId) => {
    try {
      setError("");
      setVoting(true);
      const res = await fetch(`${API_BASE_URL}/api/vote/${optionId}`, {
        method: "POST",
      });
      if (!res.ok) {
        throw new Error(`Vote failed: ${res.status}`);
      }
      // After voting, refresh data
      await fetchVotes();
    } catch (err) {
      console.error(err);
      setError("Failed to register vote. Try again.");
    } finally {
      setVoting(false);
    }
  };

  useEffect(() => {
    fetchVotes();
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "#0f172a",
        color: "#e5e7eb",
        padding: "1rem",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "480px",
          background: "#020617",
          borderRadius: "16px",
          padding: "1.5rem",
          boxShadow: "0 20px 40px rgba(0,0,0,0.5)",
          border: "1px solid #1f2937",
        }}
      >
        <h1 style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>
          Simple Vote App
        </h1>
        <p style={{ fontSize: "0.9rem", color: "#9ca3af", marginBottom: "1rem" }}>
          Backend: FastAPI + AWS S3 | Frontend: React + Vite
        </p>

        {loading ? (
          <p>Loading votes…</p>
        ) : (
          <>
            <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem" }}>
              {question}
            </h2>

            {error && (
              <div
                style={{
                  background: "#7f1d1d",
                  color: "#fecaca",
                  padding: "0.5rem 0.75rem",
                  borderRadius: "8px",
                  fontSize: "0.85rem",
                  marginBottom: "0.75rem",
                }}
              >
                {error}
              </div>
            )}

            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {options.map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => handleVote(opt.id)}
                  disabled={voting}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "0.75rem 1rem",
                    borderRadius: "999px",
                    border: "1px solid #4b5563",
                    background: "#020617",
                    color: "#e5e7eb",
                    fontWeight: 500,
                    cursor: voting ? "not-allowed" : "pointer",
                    opacity: voting ? 0.7 : 1,
                    transition: "transform 0.1s ease, box-shadow 0.1s ease",
                  }}
                  onMouseDown={(e) => {
                    e.currentTarget.style.transform = "scale(0.98)";
                  }}
                  onMouseUp={(e) => {
                    e.currentTarget.style.transform = "scale(1)";
                  }}
                >
                  <span>
                    {opt.label} ({opt.id})
                  </span>
                  <span
                    style={{
                      background: "#111827",
                      borderRadius: "999px",
                      padding: "0.25rem 0.75rem",
                      fontSize: "0.85rem",
                    }}
                  >
                    {opt.votes} votes
                  </span>
                </button>
              ))}
            </div>

            <p
              style={{
                marginTop: "1rem",
                fontSize: "0.9rem",
                color: "#9ca3af",
              }}
            >
              Total votes: <strong>{totalVotes}</strong>
            </p>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
