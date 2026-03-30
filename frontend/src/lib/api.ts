import axios from "axios"
export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })
api.interceptors.request.use((config) => { const token = localStorage.getItem("token"); const tenantId = localStorage.getItem("tenant_id"); if (token) config.headers.Authorization = `Bearer ${token}`; if (tenantId) config.headers["X-Tenant-ID"] = tenantId; return config })
