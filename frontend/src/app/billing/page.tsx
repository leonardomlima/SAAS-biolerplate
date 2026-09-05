import { useMutation, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"
import { api } from "../../lib/api"
import { Link, useNavigate } from "react-router-dom"
import { ArrowLeft, CreditCard, ExternalLink, Loader2, CheckCircle2 } from "lucide-react"

type Plan = { id: string; name: string; amount: number; billing_cycle: string }
type Subscription = { status: string; plan_id: string; value: number; next_due_date?: string | null }

export default function BillingPage() {
  const navigate = useNavigate()
  
  const plansQuery = useQuery({
    queryKey: ["billing-plans"],
    queryFn: async () => (await api.get<Plan[]>("/api/v1/billing/plans")).data,
  })

  const subscriptionQuery = useQuery({
    queryKey: ["billing-subscription"],
    queryFn: async () => (await api.get<Subscription>("/api/v1/billing/subscription")).data,
    retry: false,
  })

  const checkoutMutation = useMutation({
    mutationFn: async (planId: string) => (await api.post("/api/v1/billing/checkout", { plan_id: planId })).data,
    onSuccess: () => {
      toast.success("Checkout iniciado com sucesso")
      subscriptionQuery.refetch()
    },
    onError: () => toast.error("Falha ao iniciar checkout"),
  })

  const portalMutation = useMutation({
    mutationFn: async () => (await api.post<{ portal_url: string }>("/api/v1/billing/portal", {})).data,
    onSuccess: (data) => {
      toast.success("Redirecionando para portal")
      window.open(data.portal_url, "_blank")
    },
    onError: () => toast.error("Falha ao abrir portal"),
  })

  return (
    <div className="min-h-screen bg-muted/20">
      <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:px-6">
        <button onClick={() => navigate(-1)} className="mr-2 inline-flex items-center justify-center rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex items-center gap-2 font-semibold">
          <CreditCard className="h-5 w-5" />
          <span>Faturamento e Assinatura</span>
        </div>
      </header>
      
      <main className="flex-1 space-y-8 p-4 sm:p-8 md:p-12 max-w-6xl mx-auto">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Billing ASAAS</h1>
          <p className="text-muted-foreground mt-2">Gerencie sua assinatura, informações de pagamento e faturas.</p>
        </div>

        <section className="rounded-xl border bg-card text-card-foreground shadow-sm overflow-hidden">
          <div className="flex flex-col space-y-1.5 p-6 border-b bg-muted/30">
            <h2 className="text-xl font-semibold tracking-tight">Assinatura Atual</h2>
          </div>
          <div className="p-6">
            {subscriptionQuery.isLoading ? (
              <div className="flex items-center space-x-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Carregando detalhes da assinatura...</span>
              </div>
            ) : subscriptionQuery.isError ? (
              <div className="rounded-md bg-muted p-4">
                <p className="text-sm text-muted-foreground">Nenhuma assinatura ativa encontrada para este tenant.</p>
              </div>
            ) : subscriptionQuery.data ? (
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Plano</p>
                    <p className="text-2xl font-bold">{subscriptionQuery.data.plan_id}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Status</p>
                      <div className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold bg-green-500/10 text-green-700 mt-1">
                        {subscriptionQuery.data.status}
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Valor</p>
                      <p className="text-base font-medium mt-1">R$ {subscriptionQuery.data.value.toFixed(2)}</p>
                    </div>
                  </div>
                  {subscriptionQuery.data.next_due_date && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Próximo Vencimento</p>
                      <p className="text-base mt-1">{subscriptionQuery.data.next_due_date}</p>
                    </div>
                  )}
                </div>
                <div className="flex flex-col items-start md:items-end justify-center space-y-4">
                  <button
                    className="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50"
                    disabled={portalMutation.isPending}
                    onClick={() => portalMutation.mutate()}
                    type="button"
                  >
                    {portalMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <ExternalLink className="mr-2 h-4 w-4" />}
                    {portalMutation.isPending ? "Abrindo portal..." : "Acessar Portal do ASAAS"}
                  </button>
                  <p className="text-xs text-muted-foreground text-left md:text-right max-w-xs">
                    No portal você pode alterar seu cartão de crédito, visualizar histórico de faturas e alterar dados.
                  </p>
                </div>
              </div>
            ) : null}
          </div>
        </section>

        <section>
          <div className="mb-6">
            <h2 className="text-xl font-semibold tracking-tight">Planos Disponíveis</h2>
            <p className="text-sm text-muted-foreground mt-1">Escolha o plano ideal para suas necessidades.</p>
          </div>
          
          {plansQuery.isLoading && (
            <div className="flex items-center space-x-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Carregando planos...</span>
            </div>
          )}
          
          {plansQuery.isError && (
             <div className="rounded-md bg-destructive/10 p-4">
              <p className="text-sm text-destructive">Erro ao carregar planos disponíveis.</p>
            </div>
          )}

          <div className="grid gap-6 md:grid-cols-3">
            {plansQuery.data?.map((plan) => (
              <article className="flex flex-col rounded-xl border bg-card text-card-foreground shadow-sm transition-all hover:border-primary/50" key={plan.id}>
                <div className="p-6 flex-1">
                  <h3 className="text-xl font-bold">{plan.name}</h3>
                  <div className="mt-4 flex items-baseline text-3xl font-bold">
                    R$ {plan.amount.toFixed(2)}
                    <span className="ml-1 text-sm font-medium text-muted-foreground">/ {plan.billing_cycle.toLowerCase()}</span>
                  </div>
                  <ul className="mt-6 space-y-3 text-sm text-muted-foreground">
                    <li className="flex items-center"><CheckCircle2 className="mr-2 h-4 w-4 text-primary" /> Acesso a todo o sistema</li>
                    <li className="flex items-center"><CheckCircle2 className="mr-2 h-4 w-4 text-primary" /> Suporte prioritário</li>
                    {plan.amount > 50 && <li className="flex items-center"><CheckCircle2 className="mr-2 h-4 w-4 text-primary" /> Multi-organizations</li>}
                  </ul>
                </div>
                <div className="p-6 pt-0 mt-auto">
                  <button
                    className="w-full inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50"
                    disabled={checkoutMutation.isPending}
                    onClick={() => checkoutMutation.mutate(plan.id)}
                    type="button"
                  >
                    {checkoutMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                    {checkoutMutation.isPending ? "Processando..." : "Assinar plano"}
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}
