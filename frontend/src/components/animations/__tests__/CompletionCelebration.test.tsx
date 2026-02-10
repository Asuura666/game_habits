import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { CompletionCelebration } from '../CompletionCelebration'

const mockResult = {
  xpEarned: 25,
  coinsEarned: 10,
  newStreak: 5,
  isPersonalBest: false,
}

describe('CompletionCelebration', () => {
  it('renders XP earned when shown', () => {
    render(<CompletionCelebration show={true} result={mockResult} />)
    expect(screen.getByText('+25 XP')).toBeInTheDocument()
  })

  it('renders coins earned', () => {
    render(<CompletionCelebration show={true} result={mockResult} />)
    expect(screen.getByText('+10')).toBeInTheDocument()
  })

  it('renders streak', () => {
    render(<CompletionCelebration show={true} result={mockResult} />)
    expect(screen.getByText(/Streak: 5/)).toBeInTheDocument()
  })

  it('shows RECORD badge for personal best', () => {
    const recordResult = { ...mockResult, isPersonalBest: true }
    render(<CompletionCelebration show={true} result={recordResult} />)
    expect(screen.getByText('RECORD!')).toBeInTheDocument()
  })

  it('does not render when not shown', () => {
    render(<CompletionCelebration show={false} result={mockResult} />)
    expect(screen.queryByText('+25 XP')).not.toBeInTheDocument()
  })

  it('calls onComplete after animation', async () => {
    vi.useFakeTimers()
    const onComplete = vi.fn()
    
    render(
      <CompletionCelebration
        show={true}
        result={mockResult}
        onComplete={onComplete}
      />
    )
    
    vi.advanceTimersByTime(3000)
    expect(onComplete).toHaveBeenCalled()
    
    vi.useRealTimers()
  })
})
