import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { isAuthenticated, logout } from "../services/api.js";

export default function NavigationMenu() {
  const navigate = useNavigate();
  const authed = isAuthenticated();

  function handleLogout() {
    logout().finally(() => navigate("/login"));
  }

  return (
    <nav className="navbar">
      <div>
        <Link to="/">Chat</Link>
        {authed && <Link to="/dashboard">Dashboard</Link>}
        {authed && <Link to="/documents">Documents</Link>}
      </div>
      <div>
        {authed ? (
          <button className="btn" onClick={handleLogout}>Logout</button>
        ) : (
          <Link to="/login">Admin Login</Link>
        )}
      </div>
    </nav>
  );
}
