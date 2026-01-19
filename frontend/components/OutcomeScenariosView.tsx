import { OutcomeSimulation, ScenarioType } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { TrendingUp, TrendingDown, Minus, Clock, Target } from 'lucide-react'
import { motion } from 'framer-motion'
import { useState } from 'react'
import { useReducedMotion } from '@/hooks/useReducedMotion'

interface OutcomeScenariosViewProps {
  simulation: OutcomeSimulation
}

function ScenarioIcon({ type }: { type: ScenarioType }) {
  switch (type) {
    case 'best_case':
      return <TrendingUp className="h-5 w-5 text-success" />
    case 'worst_case':
      return <TrendingDown className="h-5 w-5 text-danger" />
    case 'most_likely':
      return <Minus className="h-5 w-5 text-primary" />
  }
}

function ScenarioLabel({ type }: { type: ScenarioType }) {
  switch (type) {
    case 'best_case':
      return 'Best Case'
    case 'worst_case':
      return 'Worst Case'
    case 'most_likely':
      return 'Most Likely'
  }
}

function ScenarioColor({ type }: { type: ScenarioType }) {
  switch (type) {
    case 'best_case':
      return 'border-success bg-success/10 dark:bg-success/20'
    case 'worst_case':
      return 'border-danger bg-danger/10 dark:bg-danger/20'
    case 'most_likely':
      return 'border-primary bg-primary/10 dark:bg-primary/20'
  }
}

export function OutcomeScenariosView({ simulation }: OutcomeScenariosViewProps) {
  const prefersReducedMotion = useReducedMotion()
  const [expandedScenario, setExpandedScenario] = useState<ScenarioType | null>(null)

  // Sort scenarios in order: best, most_likely, worst
  const sortedScenarios = [...simulation.scenarios].sort((a, b) => {
    const order = { best_case: 0, most_likely: 1, worst_case: 2 }
    return order[a.scenario] - order[b.scenario]
  })

  return (
    <div className="grid gap-6 md:grid-cols-3">
      {sortedScenarios.map((scenario, index) => {
        const isExpanded = expandedScenario === scenario.scenario
        
        return (
          <motion.div
            key={scenario.scenario}
            initial={prefersReducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.4, delay: index * 0.1 }}
          >
            <Card 
              className={`${ScenarioColor({ type: scenario.scenario })} border-2 transition-all duration-300 hover:shadow-lg cursor-pointer`}
              onClick={() => setExpandedScenario(isExpanded ? null : scenario.scenario)}
            >
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ScenarioIcon type={scenario.scenario} />
                  <span>{ScenarioLabel({ type: scenario.scenario })}</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm">{scenario.description}</p>

                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">Timeframe:</span>
                    <span>{scenario.timeframe_months} months</span>
                  </div>
                  
                  <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Target className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">Confidence:</span>
                      <Badge variant="outline">
                        {Math.round(scenario.confidence * 100)}%
                      </Badge>
                    </div>
                    
                    {/* Animated confidence indicator bar */}
                    <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                      <motion.div
                        className={`h-full ${
                          scenario.scenario === 'best_case' 
                            ? 'bg-success' 
                            : scenario.scenario === 'worst_case' 
                            ? 'bg-danger' 
                            : 'bg-primary'
                        }`}
                        initial={{ scaleX: 0 }}
                        animate={{ scaleX: scenario.confidence }}
                        transition={prefersReducedMotion ? { duration: 0 } : { duration: 1, delay: index * 0.1 + 0.3, ease: 'easeOut' }}
                        style={{ transformOrigin: 'left' }}
                      />
                    </div>
                  </div>
                </div>

                {/* Progressive disclosure for risks */}
                {scenario.risks.length > 0 && (
                  <motion.div
                    initial={false}
                    animate={{ 
                      scaleY: isExpanded ? 1 : 0,
                      opacity: isExpanded ? 1 : 0
                    }}
                    transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.3 }}
                    className="overflow-hidden"
                    style={{ transformOrigin: 'top' }}
                  >
                    <div className="pt-2">
                      <p className="font-medium text-sm mb-2">Risks:</p>
                      <ul className="space-y-1">
                        {scenario.risks.map((risk, i) => (
                          <motion.li 
                            key={i} 
                            className="text-sm flex items-start gap-2"
                            initial={prefersReducedMotion ? { opacity: 1, x: 0 } : { opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.2, delay: i * 0.05 }}
                          >
                            <span className="text-muted-foreground mt-0.5">•</span>
                            <span>{risk}</span>
                          </motion.li>
                        ))}
                      </ul>
                    </div>
                  </motion.div>
                )}
                
                {scenario.risks.length > 0 && (
                  <div className="text-xs text-muted-foreground text-center pt-2">
                    {isExpanded ? '▲ Click to collapse' : '▼ Click to view risks'}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )
      })}
    </div>
  )
}
