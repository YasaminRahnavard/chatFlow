import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ChakraProvider, extendTheme } from '@chakra-ui/react'
import App from './App.jsx'

// Custom theme with modern colors (moved from App.jsx)
const theme = extendTheme({
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false,
  },
  colors: {
    brand: {
      50: '#e6f3ff',
      100: '#b3daff',
      200: '#80c2ff',
      300: '#4da9ff',
      400: '#1a91ff',
      500: '#0078e6',
      600: '#005eb3',
      700: '#004580',
      800: '#002b4d',
      900: '#00121a',
    },
    purple: {
      50: '#f3e8ff',
      100: '#d9bfff',
      200: '#bf96ff',
      300: '#a56eff',
      400: '#8b45ff',
      500: '#7c3aed',
      600: '#5b21b6',
      700: '#4c1d95',
      800: '#3730a3',
      900: '#312e81',
    }
  },
  fonts: {
    heading: `-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`,
    body: `-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`,
  },
});

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  </StrictMode>,
)
