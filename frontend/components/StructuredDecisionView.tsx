import { StructuredDecision } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Target, Lock, List, Lightbulb, HelpCircle } from 'lucide-react'

interface StructuredDecisionViewProps {
  decision: StructuredDecision
}

export function StructuredDecisionView({ decision }: StructuredDecisionViewProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Decision Goal
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg">{decision.decision_goal}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lock className="h-5 w-5" />
            Constraints
          </CardTitle>
        </CardHeader>
        <CardContent>
          {decision.constraints.length > 0 ? (
            <ul className="space-y-2">
              {decision.constraints.map((constraint, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-muted-foreground mt-1">•</span>
                  <span>{constraint}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">No constraints identified</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <List className="h-5 w-5" />
            Options
          </CardTitle>
        </CardHeader>
        <CardContent>
          {decision.options.length > 0 ? (
            <ul className="space-y-2">
              {decision.options.map((option, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-muted-foreground mt-1">•</span>
                  <span>{option}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">No options identified</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Assumptions
          </CardTitle>
        </CardHeader>
        <CardContent>
          {decision.assumptions.length > 0 ? (
            <ul className="space-y-2">
              {decision.assumptions.map((assumption, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-muted-foreground mt-1">•</span>
                  <span>{assumption}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">No assumptions identified</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HelpCircle className="h-5 w-5" />
            Missing Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          {decision.missing_information.length > 0 ? (
            <ul className="space-y-2">
              {decision.missing_information.map((info, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-muted-foreground mt-1">•</span>
                  <span>{info}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted-foreground">No missing information identified</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
