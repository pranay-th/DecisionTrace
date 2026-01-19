'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { getDecision } from '@/lib/api'
import { StructuredDecisionView } from '@/components/StructuredDecisionView'
import { BiasReportView } from '@/components/BiasReportView'
import { OutcomeScenariosView } from '@/components/OutcomeScenariosView'
import { ReflectionView } from '@/components/ReflectionView'
import { PageTransition } from '@/components/PageTransition'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function DecisionDetailPage() {
  const params = useParams()
  const id = params.id as string
  const [decision, setDecision] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchDecision() {
      try {
        const data = await getDecision(id)
        setDecision(data)
      } catch (error) {
        console.error('Failed to fetch decision:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchDecision()
  }, [id])

  if (loading) {
    return (
      <PageTransition>
        <div className="min-h-screen p-8">
          <div className="max-w-6xl mx-auto">
            <p className="text-center text-muted-foreground">Loading decision...</p>
          </div>
        </div>
      </PageTransition>
    )
  }

  if (!decision) {
    return (
      <PageTransition>
        <div className="min-h-screen p-8">
          <div className="max-w-6xl mx-auto">
            <p className="text-center text-muted-foreground">Decision not found</p>
          </div>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="min-h-screen p-8">
        <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <Link href="/analysis">
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Decisions
            </Button>
          </Link>
          
          <h1 className="text-3xl font-bold mb-2">{decision.title}</h1>
          <p className="text-muted-foreground">
            Created {new Date(decision.created_at).toLocaleDateString()}
          </p>
        </div>

        <div className="space-y-8">
          <section>
            <h2 className="text-2xl font-semibold mb-4">Original Context</h2>
            <div className="p-6 border rounded-lg bg-muted/50">
              <p className="whitespace-pre-wrap">{decision.context}</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Structured Analysis</h2>
            <StructuredDecisionView decision={decision.structured_decision} />
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Bias Detection</h2>
            <BiasReportView report={decision.bias_report} />
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">Outcome Scenarios</h2>
            <OutcomeScenariosView simulation={decision.outcome_simulations} />
          </section>

          {decision.reflection_insight ? (
            <section>
              <h2 className="text-2xl font-semibold mb-4">Reflection</h2>
              <ReflectionView insight={decision.reflection_insight} />
            </section>
          ) : (
            <section>
              <div className="p-6 border rounded-lg bg-muted/50 text-center">
                <p className="text-muted-foreground mb-4">
                  No reflection yet. Add one after you've made your decision and seen the outcome.
                </p>
                <Link href={`/reflection/${decision.id}`}>
                  <Button>Add Reflection</Button>
                </Link>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
    </PageTransition>
  )
}
