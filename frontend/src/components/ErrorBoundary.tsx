'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

// Simple client-side error logger
async function logError(error: Error, errorInfo: { componentStack?: string }) {
  try {
    const payload = {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      url: typeof window !== 'undefined' ? window.location.href : 'unknown',
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : 'unknown',
      timestamp: new Date().toISOString(),
    };
    
    // Log to console in dev
    console.error('[ErrorBoundary]', payload);
    
    // Send to backend logging endpoint (could connect to monitoring)
    if (process.env.NODE_ENV === 'production') {
      await fetch('/api/log/error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).catch(() => {
        // Fail silently
      });
    }
  } catch (e) {
    console.error('Failed to log error:', e);
  }
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: { componentStack?: string }) {
    logError(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      
      return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-900 text-white">
          <div className="max-w-md text-center">
            <h2 className="text-2xl font-bold mb-4">Oops! Quelque chose s'est mal passé</h2>
            <p className="text-gray-400 mb-6">
              Une erreur inattendue s'est produite. Veuillez rafraîchir la page.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors"
            >
              Rafraîchir la page
            </button>
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-4 text-left bg-gray-800 p-4 rounded-lg">
                <summary className="cursor-pointer text-red-400">Détails de l'erreur</summary>
                <pre className="mt-2 text-xs overflow-auto text-red-300">
                  {this.state.error.message}
                  {this.state.error.stack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
