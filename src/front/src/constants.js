const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'api'

const RULES_SERVICE_URL = `${API_BASE_URL}/upload`
const RULES_EVALUATE_SERVICE_URL = `${API_BASE_URL}/evaluate`
const REPORT_SERVICE_URL = `${API_BASE_URL}/report`

export { RULES_SERVICE_URL, REPORT_SERVICE_URL,RULES_EVALUATE_SERVICE_URL }
