import { useState } from 'react'
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google'
import { Link, useNavigate } from 'react-router-dom'
import * as authService from '../services/authService'
import { useAuth } from '../context/AuthContext'

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

export default function RegisterPage() {
  const navigate = useNavigate()
  const { signInWithGoogle } = useAuth()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [error, setError] = useState('')
  const [googleError, setGoogleError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await authService.register({
        username,
        email,
        password,
        passwordConfirm
      })
      navigate(`/verify-email?email=${encodeURIComponent(email)}`)
    } catch (err) {
      setError(err.message || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogle = async (credential) => {
    if (!credential) return
    setGoogleError('')
    try {
      await signInWithGoogle(credential)
      navigate('/dashboard', { replace: true })
    } catch (e) {
      setGoogleError(e.message || 'Google sign-up failed.')
    }
  }

  const formBlock = (
    <>
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>Create account</h1>

        <div className="form-group">
          <label htmlFor="reg-username">Username</label>
          <input
            id="reg-username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="reg-email">Email</label>
          <input
            id="reg-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="reg-password">Password</label>
          <input
            id="reg-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            minLength={8}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="reg-password2">Confirm password</label>
          <input
            id="reg-password2"
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
          {loading ? 'Creating…' : 'Register'}
        </button>

        <p className="auth-links muted-text">
          <Link to="/login">Already have an account? Sign in</Link>
        </p>
      </form>

      {googleClientId && (
        <>
          {googleError ? <p className="error-message oauth-error">{googleError}</p> : null}
          <div className="oauth-block">
            <p className="muted-text oauth-divider">or sign up with</p>
            <div className="google-signin-wrap">
              <GoogleLogin
                onSuccess={(res) => void handleGoogle(res.credential)}
                onError={() => setGoogleError('Google sign-up was cancelled or failed.')}
                text="signup_with"
                shape="rectangular"
                size="large"
                width="100%"
              />
            </div>
          </div>
        </>
      )}
    </>
  )

  return (
    <main className="page centered-page">
      {googleClientId ? (
        <GoogleOAuthProvider clientId={googleClientId}>{formBlock}</GoogleOAuthProvider>
      ) : (
        formBlock
      )}
    </main>
  )
}
