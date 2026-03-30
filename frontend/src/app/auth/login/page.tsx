import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { api } from "../../../lib/api"
import { useAuthStore } from "../../../store/authStore"

const schema = z.object({
  email: z.string().email("Email inválido"),
  password: z.string().min(8, "Senha deve ter pelo menos 8 caracteres"),
})

type LoginFormData = z.infer<typeof schema>

export default function LoginPage() {
  const [serverError, setServerError] = useState<string | null>(null)
  const navigate = useNavigate()
  const location = useLocation()
  const setSession = useAuthStore((state) => state.setSession)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({ mode: "onBlur" })

  const onSubmit = async (values: LoginFormData) => {
    setServerError(null)
    const parsed = schema.safeParse(values)
    if (!parsed.success) {
      setServerError(parsed.error.issues[0]?.message ?? "Dados inválidos")
      return
    }
    try {
      const { data } = await api.post("/api/v1/auth/login", values)
      const payload = JSON.parse(atob(data.access_token.split(".")[1]))
      const tenantId = payload.tenant_id
      setSession({ accessToken: data.access_token, refreshToken: data.refresh_token, tenantId })
      toast.success("Login realizado com sucesso")
      const redirectTo = (location.state as { from?: { pathname?: string } })?.from?.pathname ?? "/dashboard"
      navigate(redirectTo)
    } catch (error) {
      setServerError("Não foi possível autenticar. Verifique suas credenciais.")
      toast.error("Falha no login")
    }
  }

  return (
    <main className="mx-auto mt-16 w-full max-w-md rounded border p-6">
      <h1 className="mb-4 text-2xl font-bold">Entrar</h1>
      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
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
          {isSubmitting ? "Entrando..." : "Entrar"}
        </button>
      </form>
      <div className="mt-4 flex items-center justify-between text-sm">
        <Link className="underline" to="/auth/register">
          Criar conta
        </Link>
        <Link className="underline" to="/auth/reset-password">
          Esqueci minha senha
        </Link>
      </div>
    </main>
  )
}
