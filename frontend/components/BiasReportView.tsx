import { BiasReport } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { useReducedMotion } from '@/hooks/useReducedMotion'

interface BiasReportViewProps {
  report: BiasReport
}

function SeverityBadge({ score }: { score: number }) {
  const percentage = Math.round(score * 100)
  
  // Color-coded severity badges: green (low), yellow (medium), red (high)
  let colorClass = 'bg-success text-success-foreground'
  let label = 'Low'
  
  if (score >= 0.7) {
    colorClass = 'bg-danger text-danger-foreground'
    label = 'High'
  } else if (score >= 0.4) {
    colorClass = 'bg-warning text-warning-foreground'
    label = 'Medium'
  }
  
  return (
    <Badge className={colorClass}>
      {label} ({percentage}%)
    </Badge>
  )
}

function SeverityMeter({ score }: { score: number }) {
  const prefersReducedMotion = useReducedMotion()
  const percentage = Math.round(score * 100)
  
  // Determine color based on severity
  let meterColor = 'bg-success'
  if (score >= 0.7) {
    meterColor = 'bg-danger'
  } else if (score >= 0.4) {
    meterColor = 'bg-warning'
  }
  
  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">Severity Level</span>
        <span className="font-medium">{percentage}%</span>
      </div>
      <div className="h-3 bg-muted rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${meterColor} rounded-full`}
          initial={{ scaleX: 0 }}
          animate={{ scaleX: percentage / 100 }}
          transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.8, ease: 'easeOut' }}
          style={{ transformOrigin: 'left' }}
        />
      </div>
    </div>
  )
}

function BiasCard({ bias, evidence }: { bias: string; evidence: string }) {
  const prefersReducedMotion = useReducedMotion()
  const [isExpanded, setIsExpanded] = useState(false)
  
  return (
    <Card className="overflow-hidden">
      <CardHeader 
        className="cursor-pointer hover:bg-muted/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{bias}</CardTitle>
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.2 }}
          >
            <ChevronDown className="h-5 w-5 text-muted-foreground" />
          </motion.div>
        </div>
      </CardHeader>
      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div
            initial={prefersReducedMotion ? { opacity: 1, scaleY: 1 } : { opacity: 0, scaleY: 0.8 }}
            animate={{ opacity: 1, scaleY: 1 }}
            exit={prefersReducedMotion ? { opacity: 1, scaleY: 1 } : { opacity: 0, scaleY: 0.8 }}
            transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.3, ease: 'easeInOut' }}
            style={{ transformOrigin: 'top' }}
          >
            <CardContent className="pt-0">
              <p className="text-sm text-muted-foreground">
                {evidence || 'No evidence provided'}
              </p>
            </CardContent>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  )
}

export function BiasReportView({ report }: BiasReportViewProps) {
  const prefersReducedMotion = useReducedMotion()
  
  if (report.detected_biases.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-muted-foreground text-center">
            No significant biases detected in this decision.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <motion.div 
        className="p-4 border rounded-lg bg-muted/50"
        initial={prefersReducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.4 }}
      >
        <div className="flex items-center gap-2 mb-4">
          <AlertTriangle className="h-5 w-5 text-warning" />
          <span className="font-semibold">Overall Severity</span>
          <div className="ml-auto">
            <SeverityBadge score={report.severity_score} />
          </div>
        </div>
        <SeverityMeter score={report.severity_score} />
      </motion.div>

      <motion.div 
        className="grid gap-4"
        initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.4, delay: 0.2 }}
      >
        {report.detected_biases.map((bias, i) => (
          <BiasCard 
            key={i} 
            bias={bias} 
            evidence={report.evidence[bias] || 'No evidence provided'} 
          />
        ))}
      </motion.div>
    </div>
  )
}
