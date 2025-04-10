// src/components/ModalForm.jsx
import React, { useState } from "react";
import "./ModalForm.css";

export default function ModalForm({ isOpen, fields, onSubmit, error }) {
  const [formValues, setFormValues] = useState({});

  const handleChange = (key, value) => {
    setFormValues((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formValues); // Ahora el modal se cerrará desde el componente padre
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">
        <h2 className="modal-title">Información adicional requerida</h2>
        {error && <p className="modal-error global">{error}</p>}
        <form onSubmit={handleSubmit}>
          {Object.entries(fields).map(([key, field]) => (
            <div className="modal-field" key={key}>
              <label>{field.text}</label>
              <input
                type={field.type === "integer" ? "number" : "text"}
                value={formValues[key] || ""}
                onChange={(e) => handleChange(key, e.target.value)}
              />
            </div>
          ))}
          <div className="modal-buttons">
            <button type="submit" className="modal-btn primary">Enviar</button>
          </div>
        </form>
      </div>
    </div>
  );
}

