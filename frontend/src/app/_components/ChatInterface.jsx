"use client"

import React, { useState, useRef, useEffect } from "react"
import { Search, FileText, Calendar, ExternalLink, MessageCircle } from 'lucide-react'
import { Send, Paperclip, Mic, Scale } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { SidebarTrigger } from "@/components/ui/sidebar"
import ReactMarkdown from 'react-markdown'
import { useAuth } from "@/contexts/AuthContext"

export function ChatInterface({ initialQuery, initialResponse, chat_id, session_name, isLoading: initialLoading }) {
  const { token } = useAuth()
  const [messages, setMessages] = useState([])
  const [resources, setResources] = useState([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [language, setLanguage] = useState("en")
  const [documentContext, setDocumentContext] = useState(null)
  const scrollAreaRef = useRef(null)

  // Initialize with document context and query when component mounts
  React.useEffect(() => {
    // Check for document context from localStorage
    const chatContext = localStorage.getItem('chatContext')
    if (chatContext) {
      try {
        const context = JSON.parse(chatContext)
        setDocumentContext(context)
        
        if (context.initialQuery) {
          setInput(context.initialQuery)
        }
        
        // Auto-trigger summary generation for document summary requests
        if (context.requestType === 'summary') {
          // Add a small delay to ensure state is set
          setTimeout(() => {
            handleDocumentSummary(context)
          }, 100)
        }
        
        // Clear the context from localStorage after using it
        localStorage.removeItem('chatContext')
      } catch (error) {
        console.error('Error parsing chat context:', error)
      }
    } else if (initialQuery) {
      setInput(initialQuery)
    }
  }, [initialQuery])

  const handleDocumentSummary = async (context) => {
    if (!context || !context.filename) return

    const userMessage = {
      id: Date.now().toString(),
      content: context.initialQuery,
      role: "user",
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      // Use the enhanced summary generation endpoint
      const summaryResponse = await fetch('http://localhost:8000/summary/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ 
          file_name: context.filename,
          language: language
        }),
      })

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
      if (context.document && context.document.url) {
        setResources([context.document.url])
      }

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
          ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ 
          query: input, 
          history: messages,
          language: language
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
      setResources(data.files || [])      

      setMessages(prev => [...prev, assistantMessage])
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

  return (
    <div className="flex flex-col h-[600px] border rounded-xl p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-2 border-b border-border/40">
        <div className="flex items-center gap-2">
          <Scale className="h-5 w-5 text-primary" />
          <h2 className="font-semibold text-foreground">Legal AI Assistant</h2>
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
      
      {/* Chat Messages */}
      <ScrollArea className="flex-1 overflow-y-auto scrollbar-hide" ref={scrollAreaRef}>
        {/* Document Context Display */}
        {documentContext && documentContext.document && (
          <div className="mb-4 p-3 bg-muted/30 rounded-lg border border-border/40">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <div className="w-12 h-16 bg-primary/10 rounded border border-border/40 flex items-center justify-center">
                  <FileText className="h-6 w-6 text-primary" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium text-sm text-foreground truncate">
                  {documentContext.document.title}
                </h3>
                <p className="text-xs text-muted-foreground mt-1">
                  {documentContext.document.category}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="secondary" className="text-xs">
                    Document Analysis
                  </Badge>
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-6 text-xs px-2"
                    onClick={() => window.open(documentContext.document.url, '_blank')}
                  >
                    <ExternalLink className="h-3 w-3 mr-1" />
                    View Original
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {messages.length === 0 && !documentContext ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <Scale className="h-10 w-10 mb-2" />
            <h2 className="text-xl font-semibold">Start your chat</h2>
            <p>Ask any legal question about Sri Lanka.</p>
          </div>
        ) : (
          <div className="space-y-4">{messages.length === 0 && documentContext && (
              <div className="text-center text-muted-foreground py-4">
                <MessageCircle className="h-8 w-8 mx-auto mb-2" />
                <p className="text-sm">Generating document summary...</p>
              </div>
            )}
            {messages.map(msg => (
              <div key={msg.id}>
                <div className={`flex ${msg.role === "user" ? "justify-end mr-10" : "justify-start ml-10"}`}>
                  <div className={`max-w-[70%] px-4 py-2 rounded-2xl ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                    <div className="whitespace-pre-wrap text-sm">
                      <ReactMarkdown
                        components={{
                          p: ({children}) => <p className="mb-2 last:mb-0">{children}</p>,
                          ul: ({children}) => <ul className="list-disc ml-4 mb-2">{children}</ul>,
                          ol: ({children}) => <ol className="list-decimal ml-4 mb-2">{children}</ol>,
                          li: ({children}) => <li className="mb-1">{children}</li>,
                          strong: ({children}) => <strong className="font-semibold">{children}</strong>,
                          em: ({children}) => <em className="italic">{children}</em>,
                          code: ({children}) => <code className="bg-gray-200 px-1 rounded text-xs">{children}</code>,
                          pre: ({children}) => <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">{children}</pre>,
                          h1: ({children}) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
                          h2: ({children}) => <h2 className="text-md font-semibold mb-2">{children}</h2>,
                          h3: ({children}) => <h3 className="text-sm font-medium mb-1">{children}</h3>,
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
                {msg.role !== "user" && Array.isArray(resources) && resources.length > 0 && (
                  <div className="mt-2 min-w-full px-2">
                    <div className="border-t pt-4">
                      <h3 className="text-lg font-semibold mb-3 text-foreground flex items-center">
                        <FileText className="h-5 w-5 mr-2" />
                        Related Documents ({resources.length})
                      </h3>
                      <div className="min-w-full grid gap-2 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
                        {resources.map((url, index) => {
                          // Extract document type and filename
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
                          // Capitalize docType and handle known types
                          let badgeText = docType
                          if (["bills", "acts", "gazettes", "constitution"].includes(docType.toLowerCase())) {
                            badgeText = docType.charAt(0).toUpperCase() + docType.slice(1)
                          } else {
                            badgeText = "PDF"
                          }
                          return (
                            <Card key={index} className="overflow-hidden hover:shadow-lg transition-all duration-200 border-border/50 hover:border-border w-full">
                              <CardContent className="p-1">
                                <div className="flex flex-col gap-2 p-2 bg-muted/20 rounded-lg border cursor-pointer hover:bg-muted/40 transition-colors" onClick={() => window.open(url, '_blank')}>
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-1 min-w-0 flex-1">
                                      <FileText className="h-3 w-3 text-primary shrink-0" />
                                      <span className="text-xs font-medium truncate">
                                        {filename || `Document ${index + 1}`}
                                      </span>
                                    </div>
                                    <Badge variant="secondary" className="text-xs ml-1 shrink-0">
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

            {(isLoading || initialLoading) && (
              <div className="flex justify-start">
                <div className="max-w-[70%] rounded-2xl bg-muted px-4 py-3 animate-pulse">
                  <div className="flex space-x-1">
                    <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"></div>
                    <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </ScrollArea>

      {/* Input Area */}
      <div className="mt-4 flex items-center space-x-2">
        <Input
          placeholder="Ask a question..."
          className="flex-1"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading || initialLoading}
        />
        <select 
          className="text-sm border border-border rounded-md px-2 py-2 bg-background text-foreground hover:bg-muted/50 transition-colors"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          disabled={isLoading || initialLoading}
        >
          <option value="en">English</option>
          <option value="si">සිංහල</option>
          <option value="ta">தமிழ்</option>
        </select>
        <Button onClick={handleSend} disabled={!input.trim() || isLoading || initialLoading}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
