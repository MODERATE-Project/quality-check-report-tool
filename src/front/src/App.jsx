import { useState } from "react";
import "./App.css";
import { RULES_SERVICE_URL, RULES_EVALUATE_SERVICE_URL } from "./constants";
import Footer from "./components/Footer";
import ModalForm from "./components/ModalForm";

export default function XMLUploader() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState({});
  const [error, setError] = useState(null);
  const [formFields, setFormFields] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const validateXML = async (xmlFile) => {
    const formData = new FormData();
    formData.append("file", xmlFile);

    try {
      const response = await fetch(RULES_SERVICE_URL, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setResults(data);

      const hasFormFields = Object.values(data).some(value => value?.text && value?.type);
      if (hasFormFields) {
        setFormFields(data);
        setIsModalOpen(true);
      }
    } catch (err) {
      setError("Error al validar el XML");
    }
  };

  const handleFormSubmit = async (formData) => {
    try {
      const payload = new FormData();
  
      // Añadir el archivo XML
      if (file) {
        payload.append("file", file);
      }
  
      // Añadir el JSON como string
      payload.append("form_data", JSON.stringify(formData));
  
      const response = await fetch(RULES_EVALUATE_SERVICE_URL, {
        method: "POST",
        body: payload, // no se pone Content-Type, fetch lo define automáticamente
      });
  
      const evaluationResult = await response.json();
      setResults((prev) => ({ ...prev, ...evaluationResult }));
      setFormFields(null);
      setIsModalOpen(false);
    } catch (err) {
      setError("Error al enviar los datos del formulario");
    }
  };
  
  const handleDrop = async (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === "text/xml") {
      setFile(droppedFile);
      setError(null);
      await validateXML(droppedFile);
    } else {
      setError("Por favor, sube un archivo XML válido.");
    }
  };

  const handleDownloadReport = () => {
    window.print();
  };

  const getStatusClass = (status, severity) => {
    if (status === 'success') return 'status-success';
    if (status === 'error') {
      return severity === 'suspected' ? 'status-suspected' : 'status-error';
    }
    return '';
  };

  return (
    <>
      <div className="content">
        <h1 className="title">Datos Energéticos del Edificio</h1>

        <div
          className="drag-xml-box"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          {file ? file.name : "Arrastra y suelta el archivo XML aquí"}
        </div>

        {error && <p style={{ color: "red" }}>{error}</p>}

        <ModalForm
          isOpen={isModalOpen}
          fields={formFields || {}}
          onSubmit={handleFormSubmit}
        />

        {results && Object.keys(results).length > 0 && (
          <button className="button" onClick={handleDownloadReport}>
            Generar Informe
          </button>
        )}

        <div className="results">
          <h2>Resultados</h2>

          {results.common_rules && (
            <>
              <h3>Reglas Comunes</h3>
              {results.common_rules.map((rule, idx) => (
                <div className="rule-card" key={idx}>
                  <p><b>Regla ID:</b> {rule.rule_id}</p>
                  <p>
                    <b>Estado:</b>{" "}
                    <span className={getStatusClass(rule.status, rule.severity)}>
                      {rule.status}
                    </span>
                  </p>
                  <p><b>Mensaje:</b> {rule.message}</p>
                  <p><b>Descripción:</b> {rule.description}</p>
                </div>
              ))}
            </>
          )}

          {results.model_rules && Object.entries(results.model_rules).map(([model, rules], idx) => (
            <div key={idx}>
              <h3>Modelo: {model}</h3>
              {rules.map((rule, i) => (
                <div className="rule-card" key={i}>
                  <p><b>Regla ID:</b> {rule.rule_id}</p>
                  <p>
                    <b>Estado:</b>{" "}
                    <span className={getStatusClass(rule.status, rule.severity)}>
                      {rule.status}
                    </span>
                  </p>
                  <p><b>Mensaje:</b> {rule.message}</p>
                  <p><b>Descripción:</b> {rule.description}</p>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      <Footer />
    </>
  );
}
