// src/components/ModalForm.jsx
import React, { useState } from "react";
import "./ModalForm.css";

export default function ModalForm({ isOpen, fields, onSubmit, error, onCancel }) {
  const [formValues, setFormValues] = useState({});

  const handleChange = (key, value) => {
    setFormValues((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formValues);
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

              {field.type === "boolean" ? (
                <select
                  value={formValues[key] ?? ""}
                  onChange={(e) => handleChange(key, e.target.value === "true")}
                  required
                >
                  <option value="">Seleccione una opción</option>
                  <option value="true">Sí</option>
                  <option value="false">No</option>
                </select>
              ) : (
                <input
                  type="number"
                  step={field.type === "number" ? "any" : "1"}
                  value={formValues[key] ?? ""}
                  onChange={(e) => handleChange(key, e.target.value)}
                  required
                />
              )}

            </div>
          ))}
          <div className="modal-buttons">
            <button type="submit" className="modal-btn primary">Enviar</button>
            <button type="button" className="modal-btn" onClick={onCancel}>Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  );
}

