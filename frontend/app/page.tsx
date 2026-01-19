'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { PageTransition } from '@/components/PageTransition'

export default function Home() {
  return (
    <PageTransition>
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        <div className="max-w-2xl text-center space-y-8">
        <h1 className="text-5xl font-bold tracking-tight">
          DecisionTrace
        </h1>
        
        <p className="text-xl text-muted-foreground">
          Make better decisions through structured analysis, bias detection, and outcome simulation.
        </p>

        <div className="flex gap-4 justify-center">
          <Link href="/new">
            <Button size="lg" className="text-lg px-8">
              Create Decision
            </Button>
          </Link>
          
          <Link href="/analysis">
            <Button size="lg" variant="outline" className="text-lg px-8">
              View Decisions
            </Button>
          </Link>
        </div>

        <div className="pt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="p-6 border rounded-lg">
            <h3 className="font-semibold mb-2">Structure</h3>
            <p className="text-sm text-muted-foreground">
              Transform messy thoughts into clear decision frameworks
            </p>
          </div>
          
          <div className="p-6 border rounded-lg">
            <h3 className="font-semibold mb-2">Detect Biases</h3>
            <p className="text-sm text-muted-foreground">
              Identify cognitive biases that may cloud your judgment
            </p>
          </div>
          
          <div className="p-6 border rounded-lg">
            <h3 className="font-semibold mb-2">Simulate Outcomes</h3>
            <p className="text-sm text-muted-foreground">
              Explore best, worst, and most likely scenarios
            </p>
          </div>
        </div>
        </div>
      </div>
    </PageTransition>
  )
}
