import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function LoginForm({ onSubmit, loading, flash }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')

    try {
      await onSubmit({ username, password })
      setUsername('')
      setPassword('')
    } catch (submitError) {
      setError(submitError.message || 'Unable to login.')
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h1>portal</h1>

      {flash && <p className="welcome-text">{flash}</p>}

      <div className="form-group">
        <label htmlFor="username">Username</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          placeholder="Enter username"
          autoComplete="username"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          placeholder="Enter password"
          autoComplete="current-password"
          required
        />
      </div>

      {error && <p className="error-message">{error}</p>}

      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>

      <p className="auth-links muted-text">
        <Link to="/register">Create an account</Link>
        {' · '}
        <Link to="/forgot-password">Forgot password?</Link>
      </p>

    </form>
  )
}
