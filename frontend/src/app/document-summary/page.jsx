"use client"

import React, { useEffect, useState } from 'react'
import { DocumentSummaryChatInterface } from '../_components/DocumentSummaryChatInterface'

export default function DocumentSummaryPage() {
  const [documentContext, setDocumentContext] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get document context from localStorage
    const chatContext = localStorage.getItem('chatContext')
    if (chatContext) {
      try {
        const context = JSON.parse(chatContext)
        setDocumentContext(context)
        // Clear the context from localStorage after using it
        localStorage.removeItem('chatContext')
      } catch (error) {
        console.error('Error parsing chat context:', error)
      }
    }
    setLoading(false)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading document...</p>
        </div>
      </div>
    )
  }

  return <DocumentSummaryChatInterface documentContext={documentContext} />
}