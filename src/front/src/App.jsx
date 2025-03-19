import { useState } from "react";
import "./App.css";
import { REPORT_SERVICE_URL, RULES_SERVICE_URL } from "./constants"

export default function XMLUploader() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === "text/xml") {
      setFile(droppedFile);
      setError(null);
    } else {
      setError("Por favor, sube un archivo XML válido.");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(RULES_SERVICE_URL, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError("Error al validar el XML");
    }
  };

  const handleDownloadReport = async () => {
    try {
      const response = await fetch(REPORT_SERVICE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(results),
      });
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "informe.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      setError("Error al generar el informe");
    }
  };

  return (
    <div style={{ color: "#333", textAlign: "center", padding: "20px" }}>
      <h1 style={{ color: "#4CAF50" }}>Datos Energéticos del Edificio</h1>
      <div
        style={{
          border: "2px dashed #ccc",
          borderRadius: "20px",
          width: "300px",
          height: "200px",
          textAlign: "center",
          padding: "20px",
          margin: "50px auto",
          backgroundColor: "#fff",
        }}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        {file ? file.name : "Arrastra y suelta el archivo XML aquí"}
      </div>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <button style={{ padding: "10px", backgroundColor: "#4CAF50", color: "white", border: "none", cursor: "pointer", marginTop: "10px" }} onClick={handleUpload}>
        Validar XML
      </button>
      <div style={{
        margin: "20px auto",
        padding: "20px",
        backgroundColor: "#fff",
        borderRadius: "10px",
        boxShadow: "0 0 10px rgba(0, 0, 0, 0.1)",
        width: "80%",
        textAlign: "left",
      }}>
        <h2 style={{ borderBottom: "2px solid #4CAF50", paddingBottom: "5px", color: "#4CAF50" }}>Resultados</h2>
        {results.common_rules && (
          <>
            <h3 style={{ color: "#4CAF50" }}>Reglas Comunes</h3>
            {results.common_rules.map((rule, idx) => (
              <div key={idx} style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", marginBottom: "10px" }}>
                <p><b>Regla ID:</b> {rule.rule_id}</p>
                <p><b>Estado:</b> <span style={{ color: rule.status === 'success' ? 'green' : 'red' }}>{rule.status}</span></p>
                <p><b>Mensaje:</b> {rule.message}</p>
                <p><b>Descripción:</b> {rule.description}</p>
              </div>
            ))}
          </>
        )}
        {results.model_rules && Object.entries(results.model_rules).map(([model, rules], idx) => (
          <div key={idx}>
            <h3 style={{ color: "#4CAF50" }}>Modelo: {model}</h3>
            {rules.map((rule, i) => (
              <div key={i} style={{ padding: "10px", border: "1px solid #ccc", borderRadius: "5px", marginBottom: "10px" }}>
                <p><b>Regla ID:</b> {rule.rule_id}</p>
                <p><b>Estado:</b> <span style={{ color: rule.status === 'success' ? 'green' : 'red' }}>{rule.status}</span></p>
                <p><b>Mensaje:</b> {rule.message}</p>
                <p><b>Descripción:</b> {rule.description}</p>
              </div>
            ))}
          </div>
        ))}
      </div>
      {results.length > 0 && (
        <button style={{ padding: "10px", backgroundColor: "#008CBA", color: "white", border: "none", cursor: "pointer", marginTop: "10px" }} onClick={handleDownloadReport}>
          Generar y descargar informe
        </button>
      )}
    </div>
  );
}
