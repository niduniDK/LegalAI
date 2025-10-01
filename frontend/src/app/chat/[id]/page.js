"use client"

import { use } from 'react'
import ChatPage from '@/app/_components/chatPage'

export default function ChatSessionPage({ params }) {
  const { id } = use(params)
  
  return <ChatPage sessionId={id} />
}