"use client"

import React, { useState, useRef, useEffect } from "react"
import { FileText, MessageCircle, ExternalLink, Scale, ArrowLeft } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import ReactMarkdown from 'react-markdown'
import { useRouter } from "next/navigation"
import { useAuth } from "@/contexts/AuthContext"

export function DocumentSummaryChatInterface({ documentContext }) {
  const { token, logout } = useAuth()
  const [messages, setMessages] = useState([])
  const [resources, setResources] = useState([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [language, setLanguage] = useState("en")
  const [summaryGenerated, setSummaryGenerated] = useState(false)
  const scrollAreaRef = useRef(null)
  const router = useRouter()

  // Auto-generate summary when component mounts
  useEffect(() => {
    if (documentContext && documentContext.filename && !summaryGenerated && token) {
      console.log('Triggering handleDocumentSummary for:', documentContext.filename)
      handleDocumentSummary()
      setSummaryGenerated(true)
    }
  }, [documentContext?.filename, summaryGenerated, token])

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight
      }
    }
  }, [messages, isLoading])

  const handleDocumentSummary = async () => {
    if (!documentContext || !documentContext.filename) return
    if (!token) {
      console.warn("No authentication token available")
      return
    }
    if (isLoading) {
      console.log("Summary generation already in progress, skipping...")
      return
    }
    if (summaryGenerated) {
      console.log("Summary already generated, skipping...")
      return
    }

    console.log("Starting document summary generation for:", documentContext.filename)
    // Don't show the user's query message, just process the summary
    setIsLoading(true)

    try {
      // Use the enhanced summary generation endpoint
      const summaryResponse = await fetch('http://localhost:8000/summary/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          file_name: documentContext.filename,
          language: language
        }),
      })

      if (summaryResponse.status === 401) {
        console.error("Token expired or invalid. Please log in again.")
        logout()
        return
      }

      if (!summaryResponse.ok) {
        const errorData = await summaryResponse.json()
        console.error('Summary API Error:', errorData)
        throw new Error(`HTTP ${summaryResponse.status}: ${JSON.stringify(errorData)}`)
      }

      const summaryData = await summaryResponse.json()
      
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        content: summaryData.summary,
        role: "assistant",
        timestamp: new Date(),
      }
      
      setMessages(prev => [...prev, assistantMessage])
      
      // Set the document URL as a resource if available
      if (documentContext.document && documentContext.document.url) {
        setResources([documentContext.document.url])
      }

      console.log("Document summary generation completed successfully")

    } catch (error) {
      console.error('Error generating document summary:', error)
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I encountered an error while generating the document summary. Please try again.",
        role: "assistant",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      console.log("Setting isLoading to false")
      setIsLoading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = {
      id: Date.now().toString(),
      content: input,
      role: "user",
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/chat/get_ai_response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: input, 
          history: [...messages, userMessage],
          language: language,
          document_summary: true,
          document: documentContext.filename || null,
        }),
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        console.error('API Error:', errorData)
        throw new Error(`HTTP ${response.status}: ${JSON.stringify(errorData)}`)
      }
      
      const data = await response.json()
      
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        role: "assistant",
        timestamp: new Date(),
      }
      
      setMessages(prev => [...prev, assistantMessage])
      setResources(data.files || [])

    } catch (error) {
      console.error('Error:', error)
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I encountered an error. Please try again.",
        role: "assistant",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleGoBack = () => {
    router.push('/discover')
  }

  if (!documentContext) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">No Document Context</h2>
          <p className="text-muted-foreground mb-4">Please select a document from the discover page.</p>
          <Button onClick={handleGoBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Go to Discover
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border/40 p-4 flex-shrink-0">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={handleGoBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Discover
            </Button>
            <div className="h-6 w-px bg-border mx-2" />
            <Scale className="h-5 w-5 text-primary" />
            <h1 className="text-lg font-semibold">Document Analysis</h1>
          </div>
          <div className="flex items-center gap-2">
            <select 
              className="text-sm border border-border rounded-md px-2 py-1 bg-background text-foreground hover:bg-muted/50 transition-colors"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="si">සිංහල</option>
              <option value="ta">தமிழ்</option>
            </select>
          </div>
        </div>
        
        {/* Document Information Card */}
        <Card className="bg-muted/30 border-border/50">
          <CardContent className="p-4">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-12 bg-primary/10 rounded-lg border border-border/40 flex items-center justify-center">
                  <FileText className="h-5 w-5 text-primary" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-foreground mb-1">
                  {documentContext.document?.title || 'Document'}
                </h3>
                <p className="text-sm text-muted-foreground mb-2">
                  {documentContext.document?.category || 'Legal Document'}
                </p>
                <div className="flex items-center gap-2 mb-3">
                  <Badge variant="secondary" className="text-xs">
                    Document Analysis
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    AI Generated Summary
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-8 text-xs"
                    onClick={() => window.open(documentContext.document?.url, '_blank')}
                  >
                    <ExternalLink className="h-3 w-3 mr-1" />
                    View Original Document
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Chat Messages - Scrollable Area */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full">
          <div className="p-4">
            <div className="max-w-4xl mx-auto">
              {messages.length === 0 && !isLoading && (
                <div className="text-center text-muted-foreground py-8">
                  <MessageCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-semibold mb-2">Generating Document Summary</h3>
                  <p className="text-sm">Please wait while I analyze the document and generate a comprehensive summary for you.</p>
                </div>
              )}

              <div className="space-y-6">
                {messages.map((msg, index) => (
                  <div key={msg.id}>
                    <div className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                        msg.role === "user" 
                          ? "bg-primary text-primary-foreground" 
                          : "bg-muted border border-border/50"
                      }`}>
                        <div className="text-sm">
                          <ReactMarkdown
                            components={{
                              p: ({children}) => <p className="mb-3 last:mb-0 leading-relaxed">{children}</p>,
                              ul: ({children}) => <ul className="list-disc ml-4 mb-3 space-y-1">{children}</ul>,
                              ol: ({children}) => <ol className="list-decimal ml-4 mb-3 space-y-1">{children}</ol>,
                              li: ({children}) => <li className="leading-relaxed">{children}</li>,
                              strong: ({children}) => <strong className="font-semibold">{children}</strong>,
                              em: ({children}) => <em className="italic">{children}</em>,
                              code: ({children}) => <code className="bg-background/50 px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>,
                              pre: ({children}) => <pre className="bg-background/50 p-3 rounded-lg text-xs font-mono overflow-x-auto">{children}</pre>,
                              h1: ({children}) => <h1 className="text-lg font-bold mb-3">{children}</h1>,
                              h2: ({children}) => <h2 className="text-base font-semibold mb-2">{children}</h2>,
                              h3: ({children}) => <h3 className="text-sm font-medium mb-2">{children}</h3>,
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                    </div>

                    {/* Show related documents only for assistant messages */}
                    {msg.role === "assistant" && Array.isArray(resources) && resources.length > 0 && index === messages.length - 1 && (
                      <div className="mt-4 max-w-[80%]">
                        <div className="border-t border-border/30 pt-4">
                          <h4 className="text-sm font-medium mb-3 text-foreground flex items-center">
                            <FileText className="h-4 w-4 mr-2" />
                            Related Documents ({resources.length})
                          </h4>
                          <div className="grid gap-3 sm:grid-cols-1 md:grid-cols-2">
                            {resources.map((url, idx) => {
                              // Extract document info from URL
                              let docType = "Document"
                              let filename = ""
                              const basePath = "https://documents.gov.lk/view/"
                              if (url.startsWith(basePath)) {
                                const afterBase = url.slice(basePath.length)
                                const parts = afterBase.split("/")
                                if (parts.length > 1) {
                                  docType = parts[0]
                                  filename = parts.slice(1).join("/")
                                }
                              }

                              let badgeText = docType
                              if (["bills", "acts", "gazettes", "constitution"].includes(docType.toLowerCase())) {
                                badgeText = docType.charAt(0).toUpperCase() + docType.slice(1)
                              } else {
                                badgeText = "PDF"
                              }

                              return (
                                <Card key={idx} className="overflow-hidden hover:shadow-md transition-all duration-200 border-border/50 hover:border-border cursor-pointer">
                                  <CardContent className="p-3" onClick={() => window.open(url, '_blank')}>
                                    <div className="flex items-center gap-3">
                                      <div className="flex-shrink-0">
                                        <div className="w-8 h-10 bg-primary/10 rounded border border-border/40 flex items-center justify-center">
                                          <FileText className="h-4 w-4 text-primary" />
                                        </div>
                                      </div>
                                      <div className="flex-1 min-w-0">
                                        <p className="text-xs font-medium truncate mb-1">
                                          {filename || `Document ${idx + 1}`}
                                        </p>
                                        <Badge variant="secondary" className="text-xs">
                                          {badgeText}
                                        </Badge>
                                      </div>
                                    </div>
                                  </CardContent>
                                </Card>
                              )
                            })}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] rounded-2xl bg-muted border border-border/50 px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex space-x-1">
                          <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"></div>
                          <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                        <span className="text-xs text-muted-foreground ml-2">Analyzing document...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </ScrollArea>
      </div>

      {/* Input Area */}
      <div className="border-t border-border/40 p-4 flex-shrink-0">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-3">
            <Input
              placeholder="Ask a follow-up question about this document..."
              className="flex-1"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <Button onClick={handleSend} disabled={!input.trim() || isLoading} size="sm">
              <MessageCircle className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            You can ask follow-up questions about this document or request additional analysis.
          </p>
        </div>
      </div>
    </div>
  )
}