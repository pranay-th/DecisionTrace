'use client'

import { motion } from 'framer-motion'
import { CheckCircle2, Loader2, Circle } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useReducedMotion } from '@/hooks/useReducedMotion'

const agents = [
  { id: 'structuring', label: 'Structuring Decision', description: 'Extracting goals, constraints, and assumptions' },
  { id: 'bias', label: 'Detecting Biases', description: 'Identifying cognitive biases' },
  { id: 'outcomes', label: 'Simulating Outcomes', description: 'Generating best, worst, and likely scenarios' }
]

type StepStatus = 'pending' | 'active' | 'completed'

interface LoadingPipelineProps {
  currentStep?: number // 0-indexed, which step is currently active
}

export function LoadingPipeline({ currentStep = 0 }: LoadingPipelineProps) {
  const prefersReducedMotion = useReducedMotion()
  const [progress, setProgress] = useState(0)
  
  // Animate progress bar based on current step
  useEffect(() => {
    const targetProgress = ((currentStep + 1) / agents.length) * 100
    setProgress(targetProgress)
  }, [currentStep])
  
  const getStepStatus = (index: number): StepStatus => {
    if (index < currentStep) return 'completed'
    if (index === currentStep) return 'active'
    return 'pending'
  }
  
  const getStepColors = (status: StepStatus) => {
    switch (status) {
      case 'completed':
        return {
          border: 'border-green-500',
          bg: 'bg-green-50 dark:bg-green-950',
          text: 'text-green-900 dark:text-green-100',
          subtext: 'text-green-700 dark:text-green-300',
          icon: 'text-green-600 dark:text-green-400'
        }
      case 'active':
        return {
          border: 'border-blue-500',
          bg: 'bg-blue-50 dark:bg-blue-950',
          text: 'text-blue-900 dark:text-blue-100',
          subtext: 'text-blue-700 dark:text-blue-300',
          icon: 'text-blue-600 dark:text-blue-400'
        }
      case 'pending':
        return {
          border: 'border-gray-300 dark:border-gray-700',
          bg: 'bg-gray-50 dark:bg-gray-900',
          text: 'text-gray-600 dark:text-gray-400',
          subtext: 'text-gray-500 dark:text-gray-500',
          icon: 'text-gray-400 dark:text-gray-600'
        }
    }
  }
  
  return (
    <div className="space-y-6">
      {/* Animated Progress Bar */}
      <div className="w-full">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-foreground">
            Processing Step {currentStep + 1} of {agents.length}
          </span>
          <span className="text-sm text-muted-foreground">
            {Math.round(progress)}%
          </span>
        </div>
        <div className="h-2 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: progress / 100 }}
            transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.5, ease: 'easeInOut' }}
            style={{ transformOrigin: 'left' }}
          />
        </div>
      </div>
      
      {/* Sequential Step Indicators with Staggered Animations */}
      <div className="space-y-4">
        {agents.map((agent, index) => {
          const status = getStepStatus(index)
          const colors = getStepColors(status)
          
          return (
            <motion.div
              key={agent.id}
              className={`p-6 rounded-lg border ${colors.border} ${colors.bg}`}
              initial={prefersReducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={prefersReducedMotion ? { duration: 0 } : { 
                delay: index * 0.15,
                duration: 0.4,
                ease: 'easeOut'
              }}
            >
              <div className="flex items-start gap-4">
                {/* Icon with status-based animation */}
                <div className="mt-1">
                  {status === 'completed' && (
                    <motion.div
                      initial={prefersReducedMotion ? { scale: 1 } : { scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={prefersReducedMotion ? { duration: 0 } : { type: 'spring', stiffness: 200, damping: 15 }}
                    >
                      <CheckCircle2 className={`h-6 w-6 ${colors.icon}`} />
                    </motion.div>
                  )}
                  {status === 'active' && (
                    <motion.div
                      animate={prefersReducedMotion ? {} : { 
                        scale: [1, 1.1, 1],
                        opacity: [1, 0.8, 1]
                      }}
                      transition={prefersReducedMotion ? { duration: 0 } : { 
                        duration: 1.5,
                        repeat: Infinity,
                        ease: 'easeInOut'
                      }}
                    >
                      <Loader2 className={`h-6 w-6 ${colors.icon} animate-spin`} />
                    </motion.div>
                  )}
                  {status === 'pending' && (
                    <Circle className={`h-6 w-6 ${colors.icon}`} />
                  )}
                </div>
                
                {/* Step Content */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className={`font-semibold ${colors.text}`}>
                      {agent.label}
                    </h3>
                    {status === 'completed' && (
                      <motion.span
                        className="text-xs px-2 py-0.5 rounded-full bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300"
                        initial={prefersReducedMotion ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={prefersReducedMotion ? { duration: 0 } : { delay: 0.2 }}
                      >
                        Complete
                      </motion.span>
                    )}
                    {status === 'active' && (
                      <motion.span
                        className="text-xs px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300"
                        animate={prefersReducedMotion ? {} : { opacity: [0.6, 1, 0.6] }}
                        transition={prefersReducedMotion ? { duration: 0 } : { duration: 2, repeat: Infinity }}
                      >
                        In Progress
                      </motion.span>
                    )}
                  </div>
                  <p className={`text-sm mt-1 ${colors.subtext}`}>
                    {agent.description}
                  </p>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
      
      <motion.p 
        className="text-center text-sm text-muted-foreground mt-8"
        initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={prefersReducedMotion ? { duration: 0 } : { delay: 0.5 }}
      >
        This may take up to 60 seconds...
      </motion.p>
    </div>
  )
}
