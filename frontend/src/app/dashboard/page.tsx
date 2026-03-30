import { Link, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { useAuthStore } from "../../store/authStore"

export default function DashboardPage() {
  const navigate = useNavigate()
  const clearSession = useAuthStore((state) => state.clearSession)
  const tenantId = useAuthStore((state) => state.tenantId)

  const logout = () => {
    clearSession()
    toast.success("Sessão finalizada")
    navigate("/auth/login")
  }

  return (
    <main className="space-y-4 p-6">
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p className="text-sm text-gray-700">Tenant ativo: {tenantId ?? "não definido"}</p>
      <div className="flex gap-2">
        <Link className="rounded border px-3 py-2" to="/billing">
          Billing
        </Link>
        <Link className="rounded border px-3 py-2" to="/organizations">
          Organizations
        </Link>
        <button className="rounded bg-black px-3 py-2 text-white" onClick={logout} type="button">
          Logout
        </button>
      </div>
    </main>
  )
}
