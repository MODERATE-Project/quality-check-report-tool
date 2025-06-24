import React, { useState, useCallback, useEffect } from "react";
import { useTranslation } from 'react-i18next';
import "./ModalForm.css";

export default function ModalForm({ isOpen, fields, onSubmit, error, onCancel }) {
  const [formValues, setFormValues] = useState({});
  const { t, i18n } = useTranslation('common');
  const [localError, setLocalError] = useState(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);

  const resetLocalState = useCallback(() => {
    setFormValues({});
    setLocalError(null);
    setHasSubmitted(false);
  }, []);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Escape") {
        onCancel();            // reutilizamos la misma función
      }
    },
    [onCancel]
  );

  useEffect(() => {
    if (isOpen) {
      resetLocalState();
    }
  }, [isOpen, resetLocalState]);

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
    setHasSubmitted(true);
    
    // Verificar campos requeridos
    const missingRequired = Object.entries(fields).filter(([key, field]) => {
      return !field.optional && (formValues[key] === undefined || formValues[key] === "");
    });

    if (missingRequired.length > 0) {
      setLocalError(t("Por favor, complete todos los campos requeridos"));
      return;
    }

    onSubmit(formValues);
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
        
        {(error || localError) && <p className="modal-error global">{error || localError}</p>}
        <form onSubmit={handleSubmit} className="modal-body" noValidate>
          {Object.entries(fields).map(([key, field]) => (
            <div className="modal-field" key={key}>
              <label htmlFor={key}>{field.text[i18n.resolvedLanguage] || field.text['en']}</label>

              {field.type === "boolean" ? (
                <select
                  id={key}
                  value={formValues[key] === undefined ? "" : formValues[key]}
                  onChange={(e) => handleChange(key, e.target.value)}
                  required={!field.optional}
                  className={!field.optional && hasSubmitted && !formValues[key] ? "error" : ""}
                >
                  <option value="">Seleccione una opción</option>
                  <option value="true">Sí</option>
                  <option value="false">No</option>
                </select>
              ) : (
                <input
                  id={key}
                  type="number"
                  step={field.type === "number" ? "any" : "1"}
                  value={formValues[key] === undefined ? "" : formValues[key]}
                  onChange={(e) => handleChange(key, e.target.value)}
                  required={!field.optional}
                  className={!field.optional && hasSubmitted && !formValues[key] ? "error" : ""}
                />
              )}
              {!field.optional && hasSubmitted && !formValues[key] && (
                <span className="field-error">{t("Este campo es obligatorio")}</span>
              )}
              {field.optional && (
                <span className="field-info">{t("Este campo es opcional")}</span>
              )}
            </div>
          ))}
          <div className="modal-buttons">
            <button type="submit" className="modal-btn primary">{t('Enviar')}</button>
            <button type="button" className="modal-btn" onClick={onCancel}>{t('Cancelar')}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
