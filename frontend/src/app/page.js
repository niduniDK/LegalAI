"use client"

import { useState } from "react"
import { ChatBox } from "./_components/ChatBox"
import { ChatInterface } from "./_components/ChatInterface"

export default function HomePage() {
  const [chatStarted, setChatStarted] = useState(false)
  const [initialQuery, setInitialQuery] = useState("")

  const handleStartChat = (query) => {
    setInitialQuery(query)
    setChatStarted(true)
  }

  return (
    <div className="flex h-screen">
      <main className="flex-1 flex flex-col items-center justify-center p-8">
        <div className="w-full max-w-2xl space-y-8">
          <div className="text-center">
            <h1 className="text-4xl font-medium text-foreground mb-8">Break Legal jargon here.</h1>
          </div>

          {chatStarted ? (
            <ChatInterface />
          ) : (
            <ChatBox onStartChat={handleStartChat} />
          )}
        </div>
      </main>
    </div>
  )
}
