import * as React from "react"

// Simple theme provider without external dependencies
export function ThemeProvider({ children, defaultTheme = "dark", ...props }) {
  const [theme, setTheme] = React.useState(defaultTheme)

  React.useEffect(() => {
    // Check for saved theme
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      setTheme(savedTheme)
      document.documentElement.classList.toggle('dark', savedTheme === 'dark')
    } else {
      // Set default theme
      document.documentElement.classList.toggle('dark', defaultTheme === 'dark')
    }
  }, [defaultTheme])

  const toggleTheme = React.useCallback((newTheme) => {
    const themeToSet = newTheme || (theme === 'dark' ? 'light' : 'dark')
    setTheme(themeToSet)
    localStorage.setItem('theme', themeToSet)
    document.documentElement.classList.toggle('dark', themeToSet === 'dark')
  }, [theme])

  const value = {
    theme,
    setTheme: toggleTheme
  }

  return (
    <React.Fragment>
      {children}
    </React.Fragment>
  )
}

// Simple theme hook
export function useTheme() {
  const [theme, setTheme] = React.useState('dark')

  React.useEffect(() => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      setTheme(savedTheme)
      document.documentElement.classList.toggle('dark', savedTheme === 'dark')
    }
  }, [])

  const toggleTheme = React.useCallback((newTheme) => {
    const themeToSet = newTheme || (theme === 'dark' ? 'light' : 'dark')
    setTheme(themeToSet)
    localStorage.setItem('theme', themeToSet)
    document.documentElement.classList.toggle('dark', themeToSet === 'dark')
  }, [theme])

  return { theme, setTheme: toggleTheme }
}
