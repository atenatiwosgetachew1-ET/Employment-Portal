/**
 * Applies UI theme on <html>. "system" follows OS preference when attribute is cleared.
 */
export function applyTheme(theme) {
  const root = document.documentElement
  if (theme === 'system') {
    root.removeAttribute('data-theme')
    return
  }
  root.setAttribute('data-theme', theme)
}
