import axios from "axios"

const baseURL = import.meta.env.VITE_API_URL

export const api = axios.create({ baseURL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  const tenantId = localStorage.getItem("tenant_id")
  if (token) config.headers.Authorization = `Bearer ${token}`
  if (tenantId) config.headers["X-Tenant-ID"] = tenantId
  return config
})
