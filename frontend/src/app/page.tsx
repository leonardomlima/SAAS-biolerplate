import { Link } from "react-router-dom"
import { ArrowRight, KeyRound, CreditCard, Building2 } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-14 items-center justify-between px-4 md:px-8">
          <div className="font-bold tracking-tight">SaaS Boilerplate</div>
          <nav className="flex items-center gap-4">
            <Link className="text-sm font-medium hover:underline underline-offset-4" to="/auth/login">
              Entrar
            </Link>
            <Link className="inline-flex h-9 items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90" to="/auth/register">
              Começar Grátis
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <section className="w-full py-24 md:py-32 lg:py-48 flex justify-center text-center">
          <div className="container px-4 md:px-6">
            <div className="mx-auto max-w-[800px] flex flex-col items-center justify-center space-y-8">
              <div className="space-y-4">
                <h1 className="text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
                  Construa seu SaaS <br className="hidden sm:block" /> em tempo recorde
                </h1>
                <p className="mx-auto max-w-[600px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  Fluxo de autenticação completo, billing via ASAAS integrado e isolamento robusto de inquilinos. Tudo pronto para o seu próximo produto ir para produção.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto">
                <Link className="inline-flex h-11 items-center justify-center rounded-md bg-primary px-8 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90" to="/auth/register">
                  Testar Plataforma
                </Link>
                <Link className="group inline-flex h-11 items-center justify-center rounded-md border border-input bg-background px-8 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground" to="/auth/login">
                  Acessar Dashboard
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 bg-muted/50 border-t flex justify-center">
          <div className="container px-4 md:px-6">
            <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3 max-w-5xl mx-auto">
              <div className="flex flex-col items-center space-y-3 text-center p-6 bg-background rounded-lg border shadow-sm">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                  <KeyRound className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-bold">Autenticação</h3>
                <p className="text-muted-foreground">Sistema de login unificado com JWT, redefinição de senhas e rotas protegidas já implementadas.</p>
              </div>
              <div className="flex flex-col items-center space-y-3 text-center p-6 bg-background rounded-lg border shadow-sm">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                  <CreditCard className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-bold">Billing ASAAS</h3>
                <p className="text-muted-foreground">Planos de assinatura, checkout e integração fluida de faturamento com portal para usuários.</p>
              </div>
              <div className="flex flex-col items-center space-y-3 text-center p-6 bg-background rounded-lg border shadow-sm">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                  <Building2 className="h-6 w-6 text-primary" />
                </div>
                <h3 className="text-xl font-bold">Organizações</h3>
                <p className="text-muted-foreground">Isolamento multi-tenant real para que usuários pertençam e gerenciem seus workspaces separadamente.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
      <footer className="w-full border-t flex justify-center">
        <div className="container py-6 px-4 md:px-8 text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} SaaS Boilerplate. Todos os direitos reservados.
        </div>
      </footer>
    </div>
  )
}
