import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuthStore } from './store/authStore'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import VerifyEmail from './pages/VerifyEmail'
import Dashboard from './pages/Dashboard'
import CaseNew from './pages/CaseNew'
import CaseEdit from './pages/CaseEdit'
import Settings from './pages/Settings'
import Billing from './pages/Billing'

const qc = new QueryClient()

function ProtectedRoute({ children, requireSub = true }) {
  const { accessToken, user } = useAuthStore()
  if (!accessToken) return <Navigate to="/login" replace />
  if (user && !user.email_verified) return <Navigate to="/verify-email" replace />
  if (requireSub && user && !['active','past_due'].includes(user.subscription_status))
    return <Navigate to="/billing" replace />
  return children
}

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/dashboard" element={
            <ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/cases/new" element={
            <ProtectedRoute><CaseNew /></ProtectedRoute>} />
          <Route path="/cases/:id/edit" element={
            <ProtectedRoute><CaseEdit /></ProtectedRoute>} />
          <Route path="/settings" element={
            <ProtectedRoute requireSub={false}><Settings /></ProtectedRoute>} />
          <Route path="/billing" element={
            <ProtectedRoute requireSub={false}><Billing /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
