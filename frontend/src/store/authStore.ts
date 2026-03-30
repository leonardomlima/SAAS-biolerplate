import { create } from "zustand"

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  tenantId: string | null
  setSession: (payload: { accessToken: string; refreshToken: string; tenantId: string }) => void
  clearSession: () => void
}

const ACCESS_TOKEN_KEY = "token"
const REFRESH_TOKEN_KEY = "refresh_token"
const TENANT_ID_KEY = "tenant_id"

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: localStorage.getItem(ACCESS_TOKEN_KEY),
  refreshToken: localStorage.getItem(REFRESH_TOKEN_KEY),
  tenantId: localStorage.getItem(TENANT_ID_KEY),
  setSession: ({ accessToken, refreshToken, tenantId }) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    localStorage.setItem(TENANT_ID_KEY, tenantId)
    set({ accessToken, refreshToken, tenantId })
  },
  clearSession: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(TENANT_ID_KEY)
    set({ accessToken: null, refreshToken: null, tenantId: null })
  },
}))
