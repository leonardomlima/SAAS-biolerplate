import { Link } from "react-router-dom"

export default function LandingPage() {
  return (
    <main className="mx-auto mt-20 max-w-xl space-y-4 text-center">
      <h1 className="text-4xl font-bold">SaaS Boilerplate</h1>
      <p>Fluxo de autenticação, billing ASAAS e organizações prontos para produção.</p>
      <div className="flex justify-center gap-3">
        <Link className="rounded border px-4 py-2" to="/auth/login">
          Entrar
        </Link>
        <Link className="rounded bg-black px-4 py-2 text-white" to="/auth/register">
          Criar conta
        </Link>
      </div>
    </main>
  )
}
