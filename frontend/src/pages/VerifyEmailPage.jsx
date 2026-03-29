import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import * as authService from '../services/authService'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const [email, setEmail] = useState(() => searchParams.get('email') || '')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [resendLoading, setResendLoading] = useState(false)
  const [resendNote, setResendNote] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    const q = searchParams.get('email')
    if (q) setEmail(q)
  }, [searchParams])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await authService.verifyEmail({ email: email.trim(), code })
      setSuccess(true)
    } catch (err) {
      setError(err.message || 'Verification failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    setResendNote('')
    setError('')
    if (!email.trim()) {
      setError('Enter your email first.')
      return
    }
    setResendLoading(true)
    try {
      const data = await authService.resendVerificationCode({ email: email.trim() })
      setResendNote(data.message || 'Check your inbox.')
    } catch (err) {
      setError(err.message || 'Could not resend.')
    } finally {
      setResendLoading(false)
    }
  }

  if (success) {
    return (
      <main className="page centered-page">
        <div className="auth-form">
          <h1>Account active</h1>
          <p className="welcome-text">Your email is verified. You can sign in now.</p>
          <p className="muted-text">
            <Link to="/login">Sign in</Link>
          </p>
        </div>
      </main>
    )
  }

  return (
    <main className="page centered-page">
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>Verify your email</h1>
        <p className="muted-text">
          Enter the 6-digit code we sent to your inbox. It expires in 15 minutes.
        </p>

        <div className="form-group">
          <label htmlFor="ve-email">Email</label>
          <input
            id="ve-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="ve-code">Verification code</label>
          <input
            id="ve-code"
            type="text"
            inputMode="numeric"
            pattern="[0-9]*"
            maxLength={6}
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            placeholder="000000"
            autoComplete="one-time-code"
            required
          />
        </div>

        {error && <p className="error-message">{error}</p>}
        {resendNote && <p className="welcome-text">{resendNote}</p>}

        <button type="submit" disabled={loading}>
          {loading ? 'Verifying…' : 'Verify and activate'}
        </button>

        <p className="auth-links muted-text">
          <button
            type="button"
            className="link-button"
            onClick={() => void handleResend()}
            disabled={resendLoading}
          >
            {resendLoading ? 'Sending…' : 'Resend code'}
          </button>
          {' · '}
          <Link to="/login">Back to sign in</Link>
        </p>
      </form>
    </main>
  )
}
