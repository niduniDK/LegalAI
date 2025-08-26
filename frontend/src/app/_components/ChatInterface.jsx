"use client"

import React, { useState, useRef } from "react"
import { Send, Paperclip, Mic, Scale } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { SidebarTrigger } from "@/components/ui/sidebar"

export function ChatInterface({ initialQuery, initialResponse, isLoading: initialLoading }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const scrollAreaRef = useRef(null)

  // Initialize messages when component mounts or when initial data changes
  React.useEffect(() => {
    if (initialQuery && !messages.length) {
      const userMessage = {
        id: "initial-user",
        content: initialQuery,
        role: "user",
        timestamp: new Date(),
      }
      
      setMessages([userMessage])
      
      if (initialResponse) {
        const assistantMessage = {
          id: "initial-assistant",
          content: initialResponse,
          role: "assistant",
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, assistantMessage])
      }
    }
  }, [initialQuery, initialResponse, messages.length])

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
      const response = await fetch('http://127.0.0.1:8000/chat/get_ai_response', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: input }),
      })
      
      const data = await response.json()
      
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        role: "assistant",
        timestamp: new Date(),
      }
      
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
      {/* Chat Messages */}
      <ScrollArea className="flex-1 overflow-y-auto scrollbar-hide" ref={scrollAreaRef}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <Scale className="h-10 w-10 mb-2" />
            <h2 className="text-xl font-semibold">Start your chat</h2>
            <p>Ask any legal question about Sri Lanka.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map(msg => (
              <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end mr-10" : "justify-start ml-10"}`}>
                <div className={`max-w-[70%] px-4 py-2 rounded-2xl ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                  <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
                </div>
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
        <Button onClick={handleSend} disabled={!input.trim() || isLoading || initialLoading}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
