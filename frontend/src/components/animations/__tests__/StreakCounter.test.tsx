import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StreakCounter } from '../StreakCounter'

describe('StreakCounter', () => {
  it('renders streak number', () => {
    render(<StreakCounter streak={5} />)
    expect(screen.getByText('5')).toBeInTheDocument()
  })

  it('renders zero streak', () => {
    render(<StreakCounter streak={0} />)
    expect(screen.getByText('0')).toBeInTheDocument()
  })

  it('shows NEW badge for personal best', () => {
    render(<StreakCounter streak={10} isNewRecord={true} />)
    expect(screen.getByText('NEW!')).toBeInTheDocument()
  })

  it('does not show NEW badge when not a record', () => {
    render(<StreakCounter streak={10} isNewRecord={false} />)
    expect(screen.queryByText('NEW!')).not.toBeInTheDocument()
  })

  it('renders high streak values', () => {
    render(<StreakCounter streak={365} />)
    expect(screen.getByText('365')).toBeInTheDocument()
  })
})
