const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5501'

const RULES_SERVICE_URL = `${API_BASE_URL}/upload`
const REPORT_SERVICE_URL = `${API_BASE_URL}/report`

export { RULES_SERVICE_URL, REPORT_SERVICE_URL }
