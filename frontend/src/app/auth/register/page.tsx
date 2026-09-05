import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Link, useNavigate } from "react-router-dom"
import { toast } from "sonner"
import { api } from "../../../lib/api"
import { useAuthStore } from "../../../store/authStore"
import { Loader2 } from "lucide-react"

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
    <div className="flex min-h-screen flex-col items-center justify-center bg-muted/40 p-4">
      <div className="w-full max-w-sm rounded-xl border bg-card text-card-foreground shadow-sm">
        <div className="flex flex-col space-y-1.5 p-6 pb-4">
          <h1 className="text-2xl font-semibold tracking-tight text-center">Criar uma conta</h1>
          <p className="text-sm text-muted-foreground text-center">Preencha seus dados para começar a usar a plataforma</p>
        </div>
        <div className="p-6 pt-0">
          <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
            <div className="space-y-2">
              <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                Nome Completo
              </label>
              <input 
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" 
                placeholder="João da Silva"
                {...register("full_name")} 
              />
              {errors.full_name && <p className="text-sm text-destructive">{errors.full_name.message}</p>}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                Organização
              </label>
              <input 
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" 
                placeholder="Minha Empresa"
                {...register("organization_name")} 
              />
              {errors.organization_name && <p className="text-sm text-destructive">{errors.organization_name.message}</p>}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                Email
              </label>
              <input 
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" 
                type="email" 
                placeholder="nome@empresa.com"
                {...register("email")} 
              />
              {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                Senha
              </label>
              <input 
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" 
                type="password" 
                placeholder="••••••••"
                {...register("password")} 
              />
              {errors.password && <p className="text-sm text-destructive">{errors.password.message}</p>}
            </div>

            {serverError && (
              <div className="p-3 text-sm bg-destructive/10 text-destructive rounded-md">
                {serverError}
              </div>
            )}

            <button 
              className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 h-10 mt-2" 
              disabled={isSubmitting} 
              type="submit"
            >
               {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              {isSubmitting ? "Criando..." : "Criar conta"}
            </button>
          </form>
          <div className="mt-6 text-center text-sm text-muted-foreground">
            Já tem uma conta?{" "}
            <Link className="font-medium text-primary hover:underline underline-offset-4" to="/auth/login">
              Entrar agora
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
