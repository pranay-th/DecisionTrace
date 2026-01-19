'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { createDecision } from '@/lib/api'
import { LoadingPipeline } from '@/components/LoadingPipeline'
import { PageTransition } from '@/components/PageTransition'
import { X, Plus } from 'lucide-react'

export default function NewDecisionPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    title: '',
    context: '',
    constraints: [''],
    options: ['']
  })

  const addConstraint = () => {
    setFormData(prev => ({
      ...prev,
      constraints: [...prev.constraints, '']
    }))
  }

  const removeConstraint = (index: number) => {
    setFormData(prev => ({
      ...prev,
      constraints: prev.constraints.filter((_, i) => i !== index)
    }))
  }

  const updateConstraint = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      constraints: prev.constraints.map((c, i) => i === index ? value : c)
    }))
  }

  const addOption = () => {
    setFormData(prev => ({
      ...prev,
      options: [...prev.options, '']
    }))
  }

  const removeOption = (index: number) => {
    setFormData(prev => ({
      ...prev,
      options: prev.options.filter((_, i) => i !== index)
    }))
  }

  const updateOption = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      options: prev.options.map((o, i) => i === index ? value : o)
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      // Filter out empty constraints and options
      const cleanedData = {
        ...formData,
        constraints: formData.constraints.filter(c => c.trim() !== ''),
        options: formData.options.filter(o => o.trim() !== '')
      }

      const decision = await createDecision(cleanedData)
      router.push(`/decision/${decision.id}`)
    } catch (err: any) {
      setError(err.message || 'Failed to create decision')
      setIsSubmitting(false)
    }
  }

  const isFormValid = formData.title.trim().length >= 5 && formData.context.trim().length >= 10

  if (isSubmitting) {
    return (
      <PageTransition>
        <div className="min-h-screen flex items-center justify-center p-8">
          <div className="max-w-2xl w-full">
          <h1 className="text-3xl font-bold mb-8 text-center">Analyzing Your Decision</h1>
            <LoadingPipeline />
          </div>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="min-h-screen p-8">
        <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Create New Decision</h1>
          <p className="text-muted-foreground">
            Provide details about your decision for structured analysis
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Decision Details</CardTitle>
              <CardDescription>Start with the basics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Decision Title *</Label>
                <Input
                  id="title"
                  placeholder="e.g., Should I accept the job offer?"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                  minLength={5}
                />
                <p className="text-xs text-muted-foreground">Minimum 5 characters</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="context">Context *</Label>
                <Textarea
                  id="context"
                  placeholder="Describe your situation, what factors are involved, and why this decision matters..."
                  value={formData.context}
                  onChange={(e) => setFormData({ ...formData, context: e.target.value })}
                  required
                  minLength={10}
                  rows={6}
                />
                <p className="text-xs text-muted-foreground">Minimum 10 characters</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Constraints (Optional)</CardTitle>
              <CardDescription>What limitations or requirements do you have?</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {formData.constraints.map((constraint, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    placeholder="e.g., Must relocate within 3 months"
                    value={constraint}
                    onChange={(e) => updateConstraint(index, e.target.value)}
                  />
                  {formData.constraints.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => removeConstraint(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addConstraint}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Constraint
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Options (Optional)</CardTitle>
              <CardDescription>What choices are you considering?</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {formData.options.map((option, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    placeholder="e.g., Accept the offer"
                    value={option}
                    onChange={(e) => updateOption(index, e.target.value)}
                  />
                  {formData.options.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => removeOption(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addOption}
                className="w-full"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Option
              </Button>
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
              Analyze Decision
            </Button>
            <Button
              type="button"
              variant="outline"
              size="lg"
              onClick={() => router.push('/')}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
    </PageTransition>
  )
}
