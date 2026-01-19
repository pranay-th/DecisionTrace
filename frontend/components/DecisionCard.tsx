'use client'

import { DecisionListItem } from '@/lib/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import { Calendar, CheckCircle2 } from 'lucide-react'
import { motion } from 'framer-motion'
import { useReducedMotion } from '@/hooks/useReducedMotion'

interface DecisionCardProps {
  decision: DecisionListItem
}

export function DecisionCard({ decision }: DecisionCardProps) {
  const prefersReducedMotion = useReducedMotion()
  const date = new Date(decision.created_at)
  const formattedDate = date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })

  return (
    <Link href={`/decision/${decision.id}`}>
      <motion.div
        initial={prefersReducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.3, ease: 'easeOut' }}
        whileHover={prefersReducedMotion ? {} : { scale: 1.02 }}
      >
        <Card className="hover:shadow-lg transition-all duration-300 cursor-pointer h-full">
          <CardHeader>
            <CardTitle className="line-clamp-2">{decision.title}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>{formattedDate}</span>
            </div>
            
            {decision.has_reflection && (
              <Badge variant="default" className="gap-1">
                <CheckCircle2 className="h-3 w-3" />
                Reflected
              </Badge>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </Link>
  )
}
