import { useMemo, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import * as authService from '../services/authService'

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const uid = useMemo(() => searchParams.get('uid') || '', [searchParams])
  const token = useMemo(() => searchParams.get('token') || '', [searchParams])

  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!uid || !token) {
      setError('Invalid or expired reset link.')
      return
    }
    setLoading(true)
    try {
      await authService.confirmPasswordReset({
        uid,
        token,
        newPassword: password,
        newPasswordConfirm: passwordConfirm
      })
      navigate('/login', { replace: true, state: { flash: 'Password updated. Sign in with your new password.' } })
    } catch (err) {
      setError(err.message || 'Reset failed.')
    } finally {
      setLoading(false)
    }
  }

  if (!uid || !token) {
    return (
      <main className="page centered-page">
        <div className="auth-form">
          <h1>Reset password</h1>
          <p className="error-message">This link is invalid or incomplete.</p>
          <p className="muted-text">
            <Link to="/forgot-password">Request a new link</Link> or <Link to="/login">sign in</Link>
          </p>
        </div>
      </main>
    )
  }

  return (
    <main className="page centered-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>New password</h1>
        <p className="muted-text">Choose a strong password for your account.</p>

        <div className="form-group">
          <label htmlFor="np-password">New password</label>
          <input
            id="np-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            minLength={8}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="np-password2">Confirm password</label>
          <input
            id="np-password2"
            type="password"
            value={passwordConfirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            autoComplete="new-password"
            minLength={8}
            required
          />
        </div>

        {error && <p className="error-message">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? 'Saving…' : 'Update password'}
        </button>

        <p className="auth-links muted-text">
          <Link to="/login">Back to sign in</Link>
        </p>
      </form>
    </main>
  )
}
