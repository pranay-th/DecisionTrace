'use client'

import { useState, use } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { addReflection } from '@/lib/api'
import { ArrowLeft, Loader2 } from 'lucide-react'
import Link from 'next/link'

export default function ReflectionPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()
  const [actualOutcome, setActualOutcome] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      await addReflection(id, actualOutcome)
      router.push(`/decision/${id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to add reflection')
      setIsSubmitting(false)
    }
  }

  const isFormValid = actualOutcome.trim().length >= 20

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <Link href={`/decision/${id}`}>
            <Button variant="ghost" size="sm" className="mb-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Decision
            </Button>
          </Link>
          
          <h1 className="text-3xl font-bold mb-2">Add Reflection</h1>
          <p className="text-muted-foreground">
            Share what actually happened and learn from your decision
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Actual Outcome</CardTitle>
              <CardDescription>
                Describe what happened after you made your decision
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="outcome">What was the actual outcome? *</Label>
                <Textarea
                  id="outcome"
                  placeholder="Describe what happened, how it compared to your expectations, and any surprises..."
                  value={actualOutcome}
                  onChange={(e) => setActualOutcome(e.target.value)}
                  required
                  minLength={20}
                  rows={8}
                />
                <p className="text-xs text-muted-foreground">
                  Minimum 20 characters. Be specific about what happened.
                </p>
              </div>
            </CardContent>
          </Card>

          {error && (
            <div className="p-4 border border-red-500 bg-red-50 text-red-900 rounded-lg">
              <p className="font-semibold">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          )}

          <div className="flex gap-4">
            <Button
              type="submit"
              size="lg"
              disabled={!isFormValid || isSubmitting}
              className="flex-1"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating Insights...
                </>
              ) : (
                'Generate Reflection'
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              size="lg"
              onClick={() => router.push(`/decision/${id}`)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
