import { ReflectionInsight } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Target, Lightbulb, TrendingUp } from 'lucide-react'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/hooks/useReducedMotion'

interface ReflectionViewProps {
  insight: ReflectionInsight
}

function AccuracyBadge({ score }: { score: number }) {
  const prefersReducedMotion = useReducedMotion()
  const percentage = Math.round(score * 100)
  
  let variant: 'default' | 'secondary' | 'destructive' | 'outline' = 'secondary'
  let label = 'Low Accuracy'
  let gaugeColor = 'bg-red-500'
  
  if (score >= 0.8) {
    variant = 'default'
    label = 'High Accuracy'
    gaugeColor = 'bg-green-500'
  } else if (score >= 0.5) {
    variant = 'outline'
    label = 'Moderate Accuracy'
    gaugeColor = 'bg-yellow-500'
  }
  
  return (
    <div className="flex flex-col items-end gap-2">
      <Badge variant={variant} className="text-base px-4 py-1">
        {label} ({percentage}%)
      </Badge>
      {/* Animated accuracy gauge */}
      <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${gaugeColor}`}
          initial={{ scaleX: 0 }}
          animate={{ scaleX: percentage / 100 }}
          transition={prefersReducedMotion ? { duration: 0 } : { duration: 1, ease: 'easeOut' }}
          style={{ transformOrigin: 'left' }}
        />
      </div>
    </div>
  )
}

export function ReflectionView({ insight }: ReflectionViewProps) {
  const prefersReducedMotion = useReducedMotion()
  
  // Animation variants for staggered list items
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: prefersReducedMotion ? { duration: 0 } : {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: prefersReducedMotion ? { duration: 0 } : { duration: 0.3 }
    }
  }

  // Animation variants for highlighted patterns
  const patternVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: prefersReducedMotion ? { duration: 0 } : { duration: 0.3 }
    },
    hover: prefersReducedMotion ? {} : {
      scale: 1.02,
      backgroundColor: 'rgba(var(--accent), 0.1)',
      transition: { duration: 0.2 }
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Prediction Accuracy
            </div>
            <AccuracyBadge score={insight.accuracy_score} />
          </CardTitle>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Lessons Learned
          </CardTitle>
        </CardHeader>
        <CardContent>
          <motion.ul 
            className="space-y-3"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {insight.lessons_learned.map((lesson, i) => (
              <motion.li 
                key={i} 
                className="flex items-start gap-2"
                variants={itemVariants}
              >
                <span className="text-muted-foreground mt-1">•</span>
                <span>{lesson}</span>
              </motion.li>
            ))}
          </motion.ul>
        </CardContent>
      </Card>

      {insight.repeated_patterns.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Repeated Patterns
            </CardTitle>
          </CardHeader>
          <CardContent>
            <motion.ul 
              className="space-y-3"
              variants={containerVariants}
              initial="hidden"
              animate="visible"
            >
              {insight.repeated_patterns.map((pattern, i) => (
                <motion.li 
                  key={i} 
                  className="flex items-start gap-2 p-2 rounded-md cursor-pointer"
                  variants={patternVariants}
                  whileHover="hover"
                >
                  <span className="text-muted-foreground mt-1">•</span>
                  <span>{pattern}</span>
                </motion.li>
              ))}
            </motion.ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
