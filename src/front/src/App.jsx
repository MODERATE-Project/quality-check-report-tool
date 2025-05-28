import { useState } from "react";
import "./App.css";
import { RULES_SERVICE_URL, RULES_EVALUATE_SERVICE_URL } from "./constants";
import Footer from "./components/Footer";
import ModalForm from "./components/ModalForm";
import RuleCard from "./components/RuleCard";
import { useTranslation } from 'react-i18next';
import esFlag from './assets/es-flag.svg';
import enFlag from './assets/en-flag.svg';

export default function XMLUploader() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState({});
  const [error, setError] = useState(null);
  const [formFields, setFormFields] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formError, setFormError] = useState(null);
  const [debugMode, setDebugMode] = useState(false);
  const [showSucceeded, setShowSucceeded] = useState(false);
  const { t, i18n } = useTranslation('common');


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
      setError(t("Error al validar el XML"));
    }
  };

  const handleFormSubmit = async (formData) => {
    try {
      const payload = new FormData();
      if (file) payload.append("file", file);
      payload.append("form_data", JSON.stringify(formData));

      const response = await fetch(RULES_EVALUATE_SERVICE_URL, {
        method: "POST",
        body: payload,
      });

      if (!response.ok) {
        throw new Error(t("Error al evaluar los datos. Intenta nuevamente."));
      }

      const evaluationResult = await response.json();
      
      const sortedEvaluationResult = sortRulesObject(evaluationResult);

      setResults(sortedEvaluationResult); //(prev) => ({ ...prev, ...sortedEvaluationResult }));
      setFormFields(null);
      setIsModalOpen(false);
      setFormError(null);
    } catch (err) {
      setFormError(err.message || t("Error al enviar los datos del formulario."));
    }
  };

  const sortByRuleId = arr =>
    [...arr].sort((a, b) => {
      const numA = Number(a.rule_id.replace(/\D+/g, '')); // "rule_009" → 9
      const numB = Number(b.rule_id.replace(/\D+/g, '')); // "rule_017" → 17
      return numA - numB;
    });
  
  const sortRulesObject = rulesObject =>
    Object.fromEntries(
      Object.entries(rulesObject).map(([key, value]) =>
        Array.isArray(value) ? [key, sortByRuleId(value)] : [key, value]
      )
    );
  
  const handleCancelForm = () => {
    setFormFields(null);
    setIsModalOpen(false);
    setFile(null);
    setError(null);
    setResults({});
  };


  const handleDrop = async (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === "text/xml") {
      setFile(droppedFile);
      setError(null);
      await validateXML(droppedFile);
    } else {
      setError(t("Por favor, sube un archivo XML válido."));
    }
  };

  const handleDownloadReport = () => {
    window.print();
  };


  return (
    <>
      <div className="content">
        <button 
          className="language-button"
          onClick={() => i18n.changeLanguage(i18n.language.startsWith('es') ? 'en' : 'es')}
        >
          <img 
            src={i18n.language.startsWith('es') ? enFlag : esFlag} 
            alt={i18n.language.startsWith('es') ? 'English' : 'Español'} 
            className="flag-icon"
          />
        </button>

        <h1 className="title">{t('Moderate Quality Check Tool')}</h1>
        <div style={{'textAlign':'justify'}}>
          <h2><b>{t('Acerca de')}</b></h2>
        <p>
          {t('app_description')}
        </p>

        <ul>
          <li>
            <strong style={{'color':'red'}}>{t('Errores')}</strong> {t('error_description')}
          </li>
          <li>
            <strong style={{'color':'orange'}}>{t('Sospechas de errores:')}</strong> {t('suspected_error_description')} <strong>{t("suspected_error_description_bold")}</strong>
          </li>
        </ul>
          
        </div>

        <div
          className="drag-xml-box"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
        >
          {file ? file.name : t("drag_drop_xml")}
        </div>

        {error && <p style={{ color: "red" }}>{error}</p>}

        <ModalForm
          isOpen={isModalOpen}
          fields={formFields || {}}
          onSubmit={handleFormSubmit}
          error={formError}
          onCancel={handleCancelForm}
        />

        {results && Object.keys(results).length > 0 && (
          <button className="button" onClick={handleDownloadReport}>
            {t('Generar Informe')}
          </button>
        )}

        {Object.keys(results).length > 0 &&<div className="results">
          
          
          <h2>{t('Resultados')}</h2>

          {/* Filtros */}
          <div className="filters" style={{'display':'flex', 'gap':'2rem'}}> 
              
            <label style={{ display: 'block', marginBottom: '20px' }}>
              <input
                type="checkbox"
                checked={showSucceeded}
                onChange={(e) => setShowSucceeded(e.target.checked)}
              /> {t('Mostrar todas las reglas')}
            </label>

              {import.meta.env?.MODE === 'development' && (
                <label style={{ display: 'block', marginBottom: '20px' }}>
                  <input
                    type="checkbox"
                    checked={debugMode}
                    onChange={(e) => setDebugMode(e.target.checked)}
                  /> {t('Mostrar todos los campos (DEV)')}
                </label>
              )}
  
            </div>

          {/* Reglas */}

          {results.common_rules && (
            <>
              <h3>{t('Reglas Comunes')}</h3>
              {results.common_rules.map((rule, idx) => (
                <RuleCard key={idx} rule={rule} showAllFields={debugMode} showSucceeded={showSucceeded} />
              ))}
            </>
          )}

          {results.model_rules && Object.entries(results.model_rules).map(([model, rules], idx) => (
            <div key={idx}>
              <h3>{t('Modelo')}: {model}</h3>
              {rules.map((rule, idx) => (
                <RuleCard key={idx} rule={rule} showAllFields={debugMode} showSucceeded={showSucceeded} />
              ))}
            </div>
          ))}
        </div>}
      </div>

      <Footer />
    </>
  );
}
