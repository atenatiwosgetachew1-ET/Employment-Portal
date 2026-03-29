import { useAuth } from '../context/AuthContext'

export default function DashboardPage() {
  const { user } = useAuth()

  return (
    <section className="dashboard-panel">
      <h1>Dashboard</h1>
      <p className="welcome-text">
        Welcome back{user?.username ? `, ${user.username}` : ''}.
      </p>
      <p className="muted-text">
        Use the menu on the left to open other sections (e.g. Users management).
      </p>
    </section>
  )
}
