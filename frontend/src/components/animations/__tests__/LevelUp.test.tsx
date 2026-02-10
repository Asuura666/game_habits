import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LevelUp } from '../LevelUp'

describe('LevelUp', () => {
  it('renders LEVEL UP text when shown', () => {
    render(<LevelUp show={true} newLevel={5} />)
    expect(screen.getByText('LEVEL UP!')).toBeInTheDocument()
  })

  it('renders new level number', () => {
    render(<LevelUp show={true} newLevel={10} />)
    expect(screen.getByText('Level 10')).toBeInTheDocument()
  })

  it('does not render when not shown', () => {
    render(<LevelUp show={false} newLevel={5} />)
    expect(screen.queryByText('LEVEL UP!')).not.toBeInTheDocument()
  })

  it('handles high level values', () => {
    render(<LevelUp show={true} newLevel={99} />)
    expect(screen.getByText('Level 99')).toBeInTheDocument()
  })

  it('calls onComplete after animation', async () => {
    vi.useFakeTimers()
    const onComplete = vi.fn()
    
    render(<LevelUp show={true} newLevel={5} onComplete={onComplete} />)
    
    vi.advanceTimersByTime(4000)
    expect(onComplete).toHaveBeenCalled()
    
    vi.useRealTimers()
  })
})
