import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { XPGain } from '../XPGain'

describe('XPGain', () => {
  it('renders XP amount when shown', () => {
    render(<XPGain amount={50} show={true} />)
    expect(screen.getByText('+50 XP')).toBeInTheDocument()
  })

  it('does not render when not shown', () => {
    render(<XPGain amount={50} show={false} />)
    expect(screen.queryByText('+50 XP')).not.toBeInTheDocument()
  })

  it('displays correct amount', () => {
    render(<XPGain amount={123} show={true} />)
    expect(screen.getByText('+123 XP')).toBeInTheDocument()
  })

  it('calls onComplete after animation', async () => {
    vi.useFakeTimers()
    const onComplete = vi.fn()
    
    render(<XPGain amount={50} show={true} onComplete={onComplete} />)
    
    vi.advanceTimersByTime(2000)
    expect(onComplete).toHaveBeenCalled()
    
    vi.useRealTimers()
  })
})
