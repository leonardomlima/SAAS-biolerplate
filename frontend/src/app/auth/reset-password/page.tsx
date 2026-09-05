import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Link } from "react-router-dom"
import { toast } from "sonner"
import { api } from "../../../lib/api"
import { Loader2, ArrowLeft } from "lucide-react"

const schema = z.object({
  email: z.string().email("Email inválido"),
})

type ResetPasswordFormData = z.infer<typeof schema>

export default function ResetPasswordPage() {
  const [message, setMessage] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ResetPasswordFormData>()

  const onSubmit = async (values: ResetPasswordFormData) => {
    const parsed = schema.safeParse(values)
    if (!parsed.success) {
      toast.error(parsed.error.issues[0]?.message ?? "Email inválido")
      return
    }
    await api.post("/api/v1/auth/reset-password", values)
    setMessage("Se sua conta existir, enviaremos instruções para seu email.")
    toast.success("Solicitação enviada")
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-muted/40 p-4">
      <div className="w-full max-w-sm rounded-xl border bg-card text-card-foreground shadow-sm">
        <div className="flex flex-col space-y-1.5 p-6 pb-4">
          <h1 className="text-2xl font-semibold tracking-tight text-center">Recuperar senha</h1>
          <p className="text-sm text-muted-foreground text-center">Digite seu email e enviaremos instruções</p>
        </div>
        <div className="p-6 pt-0">
          <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
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
            
            {message && (
              <div className="p-3 text-sm bg-green-500/10 text-green-700 dark:text-green-400 rounded-md">
                {message}
              </div>
            )}
            
            <button 
              className="inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 h-10 mt-2" 
              disabled={isSubmitting} 
              type="submit"
            >
              {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              {isSubmitting ? "Enviando..." : "Enviar instruções"}
            </button>
          </form>
          <div className="mt-6 text-center text-sm text-muted-foreground">
            <Link className="inline-flex items-center font-medium text-primary hover:underline underline-offset-4" to="/auth/login">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Voltar ao login
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
