import React, { useState, useCallback, useEffect } from "react";
import { useTranslation } from 'react-i18next';

import "./ModalForm.css";

export default function ModalForm({ isOpen, fields, onSubmit, error, onCancel }) {
  const [formValues, setFormValues] = useState({});
  const { t, i18n } = useTranslation('common');

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Escape") {
        onCancel();            // reutilizamos la misma función
      }
    },
    [onCancel]
  );

  useEffect(() => {
    if (!isOpen) return;        // sólo añadimos el listener cuando el modal está abierto
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, handleKeyDown]);

  const handleChange = (key, value) => {
    setFormValues((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // 1) Convertimos las claves "regla_008_0" en un objeto anidado:
    //    {
    //      "regla_008": { "0": valor },
    //      "regla_014": { "0": valor, "1": valor },
    //      ...
    //    }
    const groupedValues = Object.entries(formValues).reduce((acc, [key, val]) => {
      // key = "regla_008_0", "regla_008_1", etc.
      const lastUnderscoreIndex = key.lastIndexOf("_");
      if (lastUnderscoreIndex === -1) {
        console.warn(`Clave sin el formato esperado: ${key}`);
        return acc;
      }

      // "regla_008" y "0"
      const ruleId = key.substring(0, lastUnderscoreIndex);       // "regla_008"
      const questionIndex = key.substring(lastUnderscoreIndex + 1); // "0"

      // Creamos el objeto de la regla si no existe
      if (!acc[ruleId]) {
        acc[ruleId] = {};
      }

      // Añadimos la respuesta bajo su pregunta correspondiente
      acc[ruleId][questionIndex] = val;

      return acc;
    }, {});

    // 2) Llamamos a onSubmit con el objeto anidado
    onSubmit(groupedValues);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-container">

      <button
          className="modal-close-btn"
          aria-label="Cerrar"
          onClick={onCancel}
          type="button"
        >
          &times;
        </button>

        <h2 className="modal-title">{t('Información adicional requerida')}</h2>
        
        {error && <p className="modal-error global">{error}</p>}
        <form onSubmit={handleSubmit} className="modal-body">
          {Object.entries(fields).map(([key, field]) => (
            <div className="modal-field" key={key}>
              <label>{typeof field.text === 'object' ? field.text[i18n.language] : field.text}</label>

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
        </form>
          <div className="modal-buttons">
            <button type="submit" className="modal-btn primary" onClick={handleSubmit}>{t('Enviar')}</button>
            <button type="button" className="modal-btn" onClick={onCancel}>{t('Cancelar')}</button>
          </div>
      </div>
    </div>
  );
}
