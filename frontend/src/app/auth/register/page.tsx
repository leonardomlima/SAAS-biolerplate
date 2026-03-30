import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Link, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { api } from "../../../lib/api"
import { useAuthStore } from "../../../store/authStore"

const schema = z.object({
  full_name: z.string().min(2, "Nome obrigatório"),
  organization_name: z.string().min(2, "Empresa obrigatória"),
  email: z.string().email("Email inválido"),
  password: z.string().min(8, "Senha mínima: 8 caracteres"),
})

type RegisterFormData = z.infer<typeof schema>

export default function RegisterPage() {
  const [serverError, setServerError] = useState<string | null>(null)
  const navigate = useNavigate()
  const setSession = useAuthStore((state) => state.setSession)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>()

  const onSubmit = async (values: RegisterFormData) => {
    setServerError(null)
    const parsed = schema.safeParse(values)
    if (!parsed.success) {
      setServerError(parsed.error.issues[0]?.message ?? "Dados inválidos")
      return
    }
    try {
      const { data } = await api.post("/api/v1/auth/register", values)
      const payload = JSON.parse(atob(data.access_token.split(".")[1]))
      setSession({ accessToken: data.access_token, refreshToken: data.refresh_token, tenantId: payload.tenant_id })
      toast.success("Conta criada com sucesso")
      navigate("/dashboard")
    } catch {
      setServerError("Não foi possível criar sua conta")
      toast.error("Falha no cadastro")
    }
  }

  return (
    <main className="mx-auto mt-16 w-full max-w-md rounded border p-6">
      <h1 className="mb-4 text-2xl font-bold">Criar conta</h1>
      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
        <div>
          <label className="mb-1 block text-sm">Nome completo</label>
          <input className="w-full rounded border p-2" {...register("full_name")} />
          {errors.full_name && <p className="text-sm text-red-600">{errors.full_name.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm">Organização</label>
          <input className="w-full rounded border p-2" {...register("organization_name")} />
          {errors.organization_name && <p className="text-sm text-red-600">{errors.organization_name.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm">Email</label>
          <input className="w-full rounded border p-2" type="email" {...register("email")} />
          {errors.email && <p className="text-sm text-red-600">{errors.email.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm">Senha</label>
          <input className="w-full rounded border p-2" type="password" {...register("password")} />
          {errors.password && <p className="text-sm text-red-600">{errors.password.message}</p>}
        </div>
        {serverError && <p className="text-sm text-red-600">{serverError}</p>}
        <button className="w-full rounded bg-black px-4 py-2 text-white" disabled={isSubmitting} type="submit">
          {isSubmitting ? "Criando conta..." : "Criar conta"}
        </button>
      </form>
      <Link className="mt-4 inline-block text-sm underline" to="/auth/login">
        Já tenho conta
      </Link>
    </main>
  )
}
