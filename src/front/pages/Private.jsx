// src/front/pages/Private.jsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const API_URL = (import.meta.env.VITE_BACKEND_URL || "").replace(/\/$/, "");

export default function Private() {
  const [user, setUser] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const token = sessionStorage.getItem("token");
    if (!token) {
      navigate("/login", { replace: true });
      return;
    }
    (async () => {
      try {
        const res = await fetch(`${API_URL}/api/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          sessionStorage.clear();
          navigate("/login", { replace: true });
          return;
        }
        const data = await res.json();
        setUser(data);
      } catch (e) {
        console.error(e);
        setError("Network error while verifying user.");
      }
    })();
  }, [navigate]);

  if (error) return <div className="alert alert-danger m-3">{error}</div>;
  if (!user) return <p className="text-center mt-4">Loading…</p>;

  return (
    <div className="container py-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h3>Private Dashboard</h3>
        <button
          className="btn btn-outline-danger btn-sm"
          onClick={() => {
            sessionStorage.removeItem("token");
            sessionStorage.removeItem("user");
            navigate("/login", { replace: true });
          }}
        >
          Logout
        </button>
      </div>

      <div className="card shadow-sm">
        <div className="card-body">
          <p className="mb-1"><strong>ID:</strong> {user.id}</p>
          <p className="mb-1"><strong>Username:</strong> {user.username}</p>
          <p className="mb-0"><strong>Email:</strong> {user.email}</p>
        </div>
      </div>
    </div>
  );
}

