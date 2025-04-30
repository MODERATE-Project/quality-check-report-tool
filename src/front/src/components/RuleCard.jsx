import './RuleCard.css';

const VISIBLE_FIELDS = ['status', 'message', 'details'];

export default function RuleCard({ rule, showAllFields }) {
  const { rule_id, status, severity, message, description, details } = rule;

  const getStatusClass = () => {
    if (status === 'success') return 'status-success';
    if (status === 'error') {
      return severity?.toLowerCase() === 'suspected' ? 'status-suspected' : 'status-error';
    }
    return '';
  };

  const getStatusLabel = () => {
    if (status === 'success') return 'correcto';
    if (severity === 'suspected') return 'sospecha de error';
    return 'error';
  };

  const renderDetails = () => {
    if (!details || (typeof details === 'string' && details.trim() === '')) return null;

    if (typeof details === 'string') {
      return (
        <div>
          <b>Detalles:</b>
          <p>{details}</p>
        </div>
      );
    }

    if (typeof details === 'object') {
      return (
        <div>
          <b>Detalles:</b>
          <ul>
            {Object.entries(details).map(([key, value]) => (
              <li key={key}>
                <b>{key}:</b> {String(value)}
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

  return (
    <div className="rule-card">
      <p>
        <b>Estado:</b>{" "}
        <span className={`status ${getStatusClass()}`}>{getStatusLabel()}</span>
      </p>
      <p><b>Mensaje:</b> {message}</p>
      
      {renderDetails()}
      {renderExtraFields()}
    </div>
  );
}
