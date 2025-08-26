"use client"

import React, { useState, useRef } from "react"
import { Send, Paperclip, Mic, Scale } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { SidebarTrigger } from "@/components/ui/sidebar"

// Sample messages (starts empty)
const sampleMessages = [
    {
    id: "1",
    content: "What are the requirements for starting a business in Sri Lanka?",
    role: "user", // "user" | "assistant"
    timestamp: new Date(),
    sources: [
      {
        title: "Companies Act No. 07 of 2007",
        url: "#",
        snippet: "Requirements for company incorporation"
      }
    ]
  }
]

export function ChatInterface() {
  const [messages, setMessages] = useState(sampleMessages)
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const scrollAreaRef = useRef(null)

  const handleSend = () => {
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

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        content: "This is a simulated AI response based on your question.",
        role: "assistant",
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMessage])
      setIsLoading(false)
    }, 2000)
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
      <ScrollArea className="flex-1" ref={scrollAreaRef}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <Scale className="h-10 w-10 mb-2" />
            <h2 className="text-xl font-semibold">Start your chat</h2>
            <p>Ask any legal question about Sri Lanka.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map(msg => (
              <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[70%] px-4 py-2 rounded-2xl ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                  <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[70%] rounded-2xl bg-muted px-4 py-3 animate-pulse">
                  <div className="h-2 w-2 rounded-full bg-muted-foreground mb-1"></div>
                  <div className="h-2 w-2 rounded-full bg-muted-foreground mb-1"></div>
                  <div className="h-2 w-2 rounded-full bg-muted-foreground"></div>
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
          disabled={isLoading}
        />
        <Button onClick={handleSend} disabled={!input.trim() || isLoading}>
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}
