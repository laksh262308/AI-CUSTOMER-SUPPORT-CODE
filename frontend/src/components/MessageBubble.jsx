import React from "react";

export default function MessageBubble({ role, text }) {
  return <div className={`message ${role}`}>{text}</div>;
}
