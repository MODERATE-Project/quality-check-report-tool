import './RuleCard.css';
import { useTranslation } from 'react-i18next';

const VISIBLE_FIELDS = ['status', 'messages', 'details', 'name'];

export default function RuleCard({ rule, showAllFields, showSucceeded }) {
  const { t, i18n } = useTranslation('common');
  const { rule_id, status, severity, messages, description, details, name } = rule;

  const getStatusClass = () => {
    if (status === 'success') return 'status-success';
    if (status === 'error') {
      return severity?.toLowerCase() === 'warning' ? 'status-suspected' : 'status-error';
    }
    if (status === 'suspected') return 'status-suspected';
    
    return '';
  };

  const getStatusLabel = () => {
    if (status === 'success') return t('correcto');
    if (severity?.toLowerCase() === 'warning') return t('sospecha de error');
    return t('error');
  };

  const renderValue = (value, depth = 0) => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'object' && depth === 0) {
      if (Array.isArray(value)) {
        return (
          <ul>
            {value.map((item, index) => (
              <li key={index}>{renderValue(item, depth + 1)}</li>
            ))}
          </ul>
        );
      }
      return (
        <ul>
          {Object.entries(value).map(([k, v]) => (
            <li key={k}>
              <b>{k}:</b> {renderValue(v, depth + 1)}
            </li>
          ))}
        </ul>
      );
    }
    if (typeof value === 'object') {
      if (Array.isArray(value)) {
        return value.join(', ');
      }
      return Object.entries(value)
        .map(([k, v]) => `${k}: ${v}`)
        .join(', ');
    }
    return String(value);
  };

  const renderDetails = () => {
    if ( 
      !showAllFields && (
      !details || 
      (typeof details === 'string' && details.trim() === '') ||
      (typeof details === 'object' && Object.keys(details).length === 0))
    ) return null;

    if (typeof details === 'string') {
      return (
        <p>
          <b>{t('Detalles')}:</b> {details}
        </p>
      );
    }

    if (typeof details === 'object') {
      // Obtener los detalles en el idioma actual o usar el inglés como fallback
      const localizedDetails = details[i18n.resolvedLanguage] || details.en || details.es;
      
      if (!localizedDetails) return null;

      return (
        <div>
          <b>{t('Detalles')}:</b>
          <ul>
            {Object.entries(localizedDetails).map(([key, value]) => (
              <li key={key}>
                <b>{key}:</b> {renderValue(value)}
              </li>
            ))}
          </ul>
        </div>
      );
    }

    return null;
  };

  const renderExtraFields = () => {
    return Object.entries(rule)
      .filter(([key]) =>
        showAllFields ? true : VISIBLE_FIELDS.includes(key)
      )
      .filter(([key]) =>
        !VISIBLE_FIELDS.includes(key)
      )
      .map(([key, value]) => (
        <p key={key}>
          <b>{key}:</b> {typeof value === 'object' ? JSON.stringify(value) : String(value)}
        </p>
      ));
  };

  if (!showSucceeded && status === "success") return null

  return (
    <div className="rule-card avoid-break">
      <p><b>{t('Nombre')}:</b> {typeof name === 'object' ? name[i18n.resolvedLanguage] : name}</p>
      <p>
        <b>{t('Estado')}:</b>{" "}
        <span className={`status ${getStatusClass()}`}>{getStatusLabel()}</span>
      </p>
      <p><b>{t('Mensaje')}:</b> {messages[i18n.resolvedLanguage] || details.en || details.es}</p>

      {renderDetails()}
      {renderExtraFields()}
    </div>
  );
}
