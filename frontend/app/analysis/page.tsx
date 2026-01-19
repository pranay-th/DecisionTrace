'use client'

import { useEffect, useState } from 'react'
import { getDecisions } from '@/lib/api'
import { DecisionCard } from '@/components/DecisionCard'
import { Button } from '@/components/ui/button'
import { PageTransition } from '@/components/PageTransition'
import Link from 'next/link'
import { Plus } from 'lucide-react'

export default function AnalysisPage() {
  const [decisions, setDecisions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchDecisions() {
      try {
        const { decisions: data } = await getDecisions()
        setDecisions(data)
      } catch (error) {
        console.error('Failed to fetch decisions:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchDecisions()
  }, [])

  if (loading) {
    return (
      <PageTransition>
        <div className="min-h-screen p-8">
          <div className="max-w-6xl mx-auto">
            <p className="text-center text-muted-foreground">Loading decisions...</p>
          </div>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Your Decisions</h1>
            <p className="text-muted-foreground">
              {decisions.length} {decisions.length === 1 ? 'decision' : 'decisions'} tracked
            </p>
          </div>
          
          <Link href="/new">
            <Button size="lg">
              <Plus className="h-5 w-5 mr-2" />
              New Decision
            </Button>
          </Link>
        </div>

        {decisions.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-muted-foreground mb-6">
              No decisions yet. Create your first one to get started.
            </p>
            <Link href="/new">
              <Button size="lg">
                <Plus className="h-5 w-5 mr-2" />
                Create Decision
              </Button>
            </Link>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {decisions.map((decision) => (
              <DecisionCard key={decision.id} decision={decision} />
            ))}
          </div>
        )}
      </div>
    </div>
    </PageTransition>
  )
}
