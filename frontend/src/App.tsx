import { Navigate, Route, Routes } from "react-router-dom"
import LandingPage from "./app/page"
import LoginPage from "./app/auth/login/page"
import RegisterPage from "./app/auth/register/page"
import DashboardPage from "./app/dashboard/page"
import BillingPage from "./app/billing/page"
import OrganizationsPage from "./app/organizations/page"
export function App() { return <Routes><Route path="/" element={<LandingPage />} /><Route path="/auth/login" element={<LoginPage />} /><Route path="/auth/register" element={<RegisterPage />} /><Route path="/dashboard" element={<DashboardPage />} /><Route path="/billing" element={<BillingPage />} /><Route path="/organizations" element={<OrganizationsPage />} /><Route path="*" element={<Navigate to="/" />} /></Routes> }
