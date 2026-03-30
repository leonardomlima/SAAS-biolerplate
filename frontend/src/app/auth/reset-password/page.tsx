import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { toast } from "sonner"
import { api } from "../../../lib/api"

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
    <main className="mx-auto mt-16 w-full max-w-md rounded border p-6">
      <h1 className="mb-4 text-2xl font-bold">Recuperar senha</h1>
      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
        <div>
          <label className="mb-1 block text-sm">Email</label>
          <input className="w-full rounded border p-2" type="email" {...register("email")} />
          {errors.email && <p className="text-sm text-red-600">{errors.email.message}</p>}
        </div>
        {message && <p className="text-sm text-green-700">{message}</p>}
        <button className="w-full rounded bg-black px-4 py-2 text-white" disabled={isSubmitting} type="submit">
          {isSubmitting ? "Enviando..." : "Enviar instruções"}
        </button>
      </form>
    </main>
  )
}
