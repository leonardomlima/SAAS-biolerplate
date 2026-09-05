import { useForm } from "react-hook-form"
import { z } from "zod"
import { useMutation, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"
import { api } from "../../lib/api"
import { Link, useNavigate } from "react-router-dom"
import { ArrowLeft, Building2, Plus, Loader2 } from "lucide-react"

const schema = z.object({ name: z.string().min(2, "Nome obrigatório") })

type Organization = { id: string; name: string }
type OrgFormData = z.infer<typeof schema>

export default function OrganizationsPage() {
  const navigate = useNavigate()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<OrgFormData>()

  const organizationsQuery = useQuery({
    queryKey: ["organizations"],
    queryFn: async () => (await api.get<Organization[]>("/api/v1/organizations/")).data,
  })

  const createMutation = useMutation({
    mutationFn: async (payload: OrgFormData) => (await api.post<Organization>("/api/v1/organizations/", payload)).data,
    onSuccess: () => {
      toast.success("Organização criada")
      organizationsQuery.refetch()
      reset()
    },
    onError: () => toast.error("Falha ao criar organização"),
  })

  const onSubmit = async (values: OrgFormData) => {
    const parsed = schema.safeParse(values)
    if (!parsed.success) {
      toast.error(parsed.error.issues[0]?.message ?? "Nome inválido")
      return
    }
    await createMutation.mutateAsync(values)
  }

  return (
    <div className="min-h-screen bg-muted/20">
      <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:px-6">
        <button onClick={() => navigate(-1)} className="mr-2 inline-flex items-center justify-center rounded-md p-2 text-muted-foreground hover:bg-muted hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div className="flex items-center gap-2 font-semibold">
          <Building2 className="h-5 w-5" />
          <span>Organizações</span>
        </div>
      </header>

      <main className="flex-1 space-y-8 p-4 sm:p-8 md:p-12 max-w-5xl mx-auto">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Suas Organizações</h1>
          <p className="text-muted-foreground mt-2">Crie novos workspaces e gerencie as organizações que você participa.</p>
        </div>

        <div className="grid gap-6 md:grid-cols-[1fr_350px]">
          <section className="flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold tracking-tight">Lista de Workspaces</h2>
            </div>
            
            {organizationsQuery.isLoading ? (
               <div className="flex items-center space-x-2 text-muted-foreground p-4">
                 <Loader2 className="h-4 w-4 animate-spin" />
                 <span>Carregando organizações...</span>
               </div>
            ) : organizationsQuery.isError ? (
               <div className="rounded-md bg-destructive/10 p-4">
                  <p className="text-sm text-destructive">Erro ao carregar organizações.</p>
               </div>
            ) : (
              <div className="grid gap-4">
                {organizationsQuery.data?.length === 0 && (
                  <div className="rounded-xl border border-dashed p-8 text-center bg-card">
                    <Building2 className="mx-auto h-8 w-8 text-muted-foreground mb-3 opacity-50" />
                    <p className="text-muted-foreground">Você ainda não faz parte de nenhuma organização.</p>
                  </div>
                )}
                {organizationsQuery.data?.map((org) => (
                  <div className="flex items-center justify-between rounded-xl border bg-card text-card-foreground shadow-sm p-4 hover:shadow-md transition-all" key={org.id}>
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary font-semibold">
                        {org.name.substring(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium leading-none">{org.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">ID: {org.id.split('-')[0]}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <aside>
            <div className="rounded-xl border bg-card text-card-foreground shadow-sm sticky top-24">
              <div className="flex flex-col space-y-1.5 p-6 border-b bg-muted/30">
                <h3 className="font-semibold tracking-tight">Criar Nova Organização</h3>
                <p className="text-sm text-muted-foreground mt-1">Adicione um novo workspace para sua empresa.</p>
              </div>
              <div className="p-6">
                <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
                  <div className="space-y-2">
                    <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Nome da organização</label>
                    <input 
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" 
                      placeholder="Ex: Empresa Tech Ltda"
                      {...register("name")} 
                    />
                    {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
                  </div>
                  <button 
                    className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:opacity-50 w-full mt-2" 
                    disabled={isSubmitting || createMutation.isPending} 
                    type="submit"
                  >
                    {isSubmitting || createMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Plus className="mr-2 h-4 w-4" />}
                    {isSubmitting || createMutation.isPending ? "Criando..." : "Criar organização"}
                  </button>
                </form>
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  )
}
