import { Link, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { useAuthStore } from "../../store/authStore"
import { LogOut, LayoutDashboard, CreditCard, Building2 } from "lucide-react"

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
    <div className="min-h-screen bg-muted/20">
      <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:px-6">
        <div className="flex items-center gap-2 font-semibold">
          <LayoutDashboard className="h-5 w-5" />
          <span>SaaS Boilerplate</span>
        </div>
        <div className="ml-auto flex items-center space-x-4">
          <span className="text-sm text-muted-foreground hidden sm:inline-block">
            Tenant: {tenantId ?? "não definido"}
          </span>
          <button 
            onClick={logout}
            className="inline-flex h-9 items-center justify-center rounded-md border border-input bg-background px-3 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          >
            <LogOut className="mr-2 h-4 w-4" />
            Sair
          </button>
        </div>
      </header>
      
      <main className="flex-1 space-y-6 p-4 sm:p-8 md:p-12">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-2">Visão geral do sistema e navegação rápida.</p>
        </div>
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Link to="/billing" className="rounded-xl border bg-card text-card-foreground shadow-sm hover:shadow-md transition-all p-6 flex flex-col space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold tracking-tight text-lg">Billing</h3>
              <CreditCard className="h-5 w-5 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground">Gerencie sua assinatura, planos e faturas no ASAAS.</p>
          </Link>
          
          <Link to="/organizations" className="rounded-xl border bg-card text-card-foreground shadow-sm hover:shadow-md transition-all p-6 flex flex-col space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold tracking-tight text-lg">Organizações</h3>
              <Building2 className="h-5 w-5 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground">Altere locatários, crie novos workspaces e gerencie times.</p>
          </Link>
        </div>
      </main>
    </div>
  )
}
