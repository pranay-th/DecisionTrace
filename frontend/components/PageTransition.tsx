'use client'

import { motion } from 'framer-motion'
import { ReactNode } from 'react'
import { useReducedMotion } from '@/hooks/useReducedMotion'

interface PageTransitionProps {
  children: ReactNode
}

/**
 * PageTransition component provides smooth fade and slide animations
 * for page navigation transitions.
 * 
 * Uses Framer Motion for performant animations with:
 * - Fade in/out effect (opacity)
 * - Slide effect (x-axis translation)
 * - 0.2s transition duration
 * 
 * Respects user's prefers-reduced-motion preference by disabling
 * animations when the preference is set.
 */
export function PageTransition({ children }: PageTransitionProps) {
  const prefersReducedMotion = useReducedMotion()
  
  return (
    <motion.div
      initial={prefersReducedMotion ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={prefersReducedMotion ? { opacity: 1, x: 0 } : { opacity: 0, x: 20 }}
      transition={prefersReducedMotion ? { duration: 0 } : { 
        duration: 0.2,
        ease: 'easeInOut'
      }}
    >
      {children}
    </motion.div>
  )
}
