import { useMutation, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"
import { api } from "../../lib/api"

type Plan = { id: string; name: string; amount: number; billing_cycle: string }

type Subscription = { status: string; plan_id: string; value: number; next_due_date?: string | null }

export default function BillingPage() {
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

  if (plansQuery.isLoading) return <div className="p-6">Carregando planos...</div>
  if (plansQuery.isError) return <div className="p-6 text-red-600">Erro ao carregar planos</div>

  return (
    <main className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Billing</h1>
      <section>
        <h2 className="mb-2 text-lg font-semibold">Assinatura atual</h2>
        {subscriptionQuery.isLoading && <p>Carregando assinatura...</p>}
        {subscriptionQuery.isError && <p className="text-sm text-gray-600">Nenhuma assinatura ativa encontrada.</p>}
        {subscriptionQuery.data && (
          <div className="rounded border p-4">
            <p>Status: {subscriptionQuery.data.status}</p>
            <p>Plano: {subscriptionQuery.data.plan_id}</p>
            <p>Valor: R$ {subscriptionQuery.data.value.toFixed(2)}</p>
            {subscriptionQuery.data.next_due_date && <p>Próximo vencimento: {subscriptionQuery.data.next_due_date}</p>}
            <button
              className="mt-3 rounded border px-3 py-2"
              disabled={portalMutation.isPending}
              onClick={() => portalMutation.mutate()}
              type="button"
            >
              {portalMutation.isPending ? "Abrindo portal..." : "Abrir portal ASAAS"}
            </button>
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-2 text-lg font-semibold">Planos</h2>
        <div className="grid gap-3 md:grid-cols-3">
          {plansQuery.data?.map((plan) => (
            <article className="rounded border p-4" key={plan.id}>
              <h3 className="font-semibold">{plan.name}</h3>
              <p className="text-sm">R$ {plan.amount.toFixed(2)} / {plan.billing_cycle.toLowerCase()}</p>
              <button
                className="mt-3 rounded bg-black px-3 py-2 text-white"
                disabled={checkoutMutation.isPending}
                onClick={() => checkoutMutation.mutate(plan.id)}
                type="button"
              >
                {checkoutMutation.isPending ? "Processando..." : "Assinar"}
              </button>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}
