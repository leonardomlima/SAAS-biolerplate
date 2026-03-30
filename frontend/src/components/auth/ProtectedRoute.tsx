import { ReactElement } from "react"
import { Navigate, useLocation } from "react-router-dom"
import { useAuthStore } from "../../store/authStore"

export default function ProtectedRoute({ children }: { children: ReactElement }) {
  const location = useLocation()
  const accessToken = useAuthStore((state) => state.accessToken)

  if (!accessToken) {
    return <Navigate to="/auth/login" replace state={{ from: location }} />
  }

  return children
}
