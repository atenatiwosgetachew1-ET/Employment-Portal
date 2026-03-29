import { useState } from 'react'
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import LoginForm from '../components/auth/LoginForm'
import { useAuth } from '../context/AuthContext'

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

export default function LoginPage() {
  const { isAuthenticated, authLoading, bootstrapping, signIn, signInWithGoogle } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const [googleError, setGoogleError] = useState('')

  if (bootstrapping) {
    return (
      <main className="page centered-page">
        <p className="muted-text">Loading…</p>
      </main>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  const from = location.state?.from?.pathname || '/dashboard'

  const handleLogin = async ({ username, password }) => {
    const loggedInUser = await signIn({ username, password })

    if (loggedInUser?.username?.toLowerCase() === 'superuser') {
      navigate('/dashboard', { replace: true })
      return
    }
    navigate(from, { replace: true })
  }

  const handleGoogle = async (credential) => {
    if (!credential) return
    setGoogleError('')
    try {
      const loggedInUser = await signInWithGoogle(credential)
      if (loggedInUser?.username?.toLowerCase() === 'superuser') {
        navigate('/dashboard', { replace: true })
        return
      }
      navigate(from, { replace: true })
    } catch (e) {
      setGoogleError(e.message || 'Google sign-in failed.')
    }
  }

  const formBlock = (
    <>
      <LoginForm
        onSubmit={handleLogin}
        loading={authLoading}
        flash={location.state?.flash}
      />
      {googleClientId && (
        <>
          {googleError ? <p className="error-message oauth-error">{googleError}</p> : null}
          <div className="oauth-block">
            <p className="muted-text oauth-divider">or continue with</p>
            <div className="google-signin-wrap">
              <GoogleLogin
                onSuccess={(res) => void handleGoogle(res.credential)}
                onError={() => setGoogleError('Google sign-in was cancelled or failed.')}
                text="signin_with"
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
