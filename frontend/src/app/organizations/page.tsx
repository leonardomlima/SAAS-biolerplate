import { useForm } from "react-hook-form"
import { z } from "zod"
import { useMutation, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"
import { api } from "../../lib/api"

const schema = z.object({ name: z.string().min(2, "Nome obrigatório") })

type Organization = { id: string; name: string }
type OrgFormData = z.infer<typeof schema>

export default function OrganizationsPage() {
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
    <main className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Organizações</h1>

      <form className="max-w-md space-y-2 rounded border p-4" onSubmit={handleSubmit(onSubmit)}>
        <label className="block text-sm">Nome da organização</label>
        <input className="w-full rounded border p-2" {...register("name")} />
        {errors.name && <p className="text-sm text-red-600">{errors.name.message}</p>}
        <button className="rounded bg-black px-4 py-2 text-white" disabled={isSubmitting || createMutation.isPending} type="submit">
          {isSubmitting || createMutation.isPending ? "Criando..." : "Criar organização"}
        </button>
      </form>

      <section>
        <h2 className="mb-2 text-lg font-semibold">Lista</h2>
        {organizationsQuery.isLoading && <p>Carregando...</p>}
        {organizationsQuery.isError && <p className="text-red-600">Erro ao carregar organizações.</p>}
        <ul className="space-y-2">
          {organizationsQuery.data?.map((org) => (
            <li className="rounded border p-3" key={org.id}>
              {org.name}
            </li>
          ))}
        </ul>
      </section>
    </main>
  )
}
