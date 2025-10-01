"use client"

import * as React from "react"
import { MessageCircle, Clock, Trash2, Edit2, Plus, Calendar, FileText } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { 
  AlertDialog, 
  AlertDialogAction, 
  AlertDialogCancel, 
  AlertDialogContent, 
  AlertDialogDescription, 
  AlertDialogFooter, 
  AlertDialogHeader, 
  AlertDialogTitle, 
  AlertDialogTrigger 
} from "@/components/ui/alert-dialog"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/contexts/AuthContext"
import Link from "next/link"
import { useRouter } from "next/navigation"

export function ChatSessionsInterface() {
  const { token, logout } = useAuth()
  const router = useRouter()
  const [chatSessions, setChatSessions] = React.useState([])
  const [isLoading, setIsLoading] = React.useState(true)
  const [editingSession, setEditingSession] = React.useState(null)
  const [newSessionName, setNewSessionName] = React.useState("")
  const [isCreating, setIsCreating] = React.useState(false)
  const [language, setLanguage] = React.useState("en")

  const fetchChatSessions = async () => {
    if (!token) {
      console.warn("No authentication token available")
      setIsLoading(false)
      return
    }

    try {
      const response = await fetch("http://localhost:8000/chat-history/user_sessions", {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
      })

      if (response.status === 401) {
        console.error("Token expired or invalid. Please log in again.")
        logout()
        return
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log("Fetched chat sessions:", data)
      setChatSessions(data || [])
    } catch (error) {
      console.error('Error fetching chat sessions:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const createNewSession = async () => {
    if (!token) return

    setIsCreating(true)
    try {
      const response = await fetch("http://localhost:8000/chat-history/sessions", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          session_name: newSessionName || `New Chat - ${new Date().toLocaleDateString()}`
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const newSession = await response.json()
      console.log("Created new session:", newSession)
      
      // Refresh the sessions list
      await fetchChatSessions()
      
      // Navigate to the new chat
      router.push(`/chat/${newSession.id}`)
      
      setNewSessionName("")
    } catch (error) {
      console.error('Error creating new session:', error)
    } finally {
      setIsCreating(false)
    }
  }

  const updateSessionName = async (sessionId, newName) => {
    if (!token) return

    try {
      const response = await fetch(`http://localhost:8000/chat-history/sessions/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          session_name: newName
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Refresh the sessions list
      await fetchChatSessions()
      setEditingSession(null)
    } catch (error) {
      console.error('Error updating session name:', error)
    }
  }

  const deleteSession = async (sessionId) => {
    if (!token) return

    try {
      const response = await fetch(`http://localhost:8000/chat-history/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Refresh the sessions list
      await fetchChatSessions()
    } catch (error) {
      console.error('Error deleting session:', error)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now - date)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 1) {
      return "Today"
    } else if (diffDays === 2) {
      return "Yesterday"
    } else if (diffDays <= 7) {
      return `${diffDays - 1} days ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  React.useEffect(() => {
    fetchChatSessions()
  }, [token])

  return (
    <div className="flex h-screen flex-col overflow-y-auto">
      {/* Header */}
      <div className="border-b border-border/40 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <SidebarTrigger />
            <h1 className="text-lg font-semibold">Chat Sessions</h1>
          </div>
          
          <div className="flex items-center gap-3">
            <select 
              className="text-sm border border-border rounded-md px-2 py-1 bg-background text-foreground hover:bg-muted/50 transition-colors"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="si">සිංහල</option>
              <option value="ta">தமிழ்</option>
            </select>
            
            <Dialog>
              <DialogTrigger asChild>
                <Button className="gap-2">
                  <Plus className="h-4 w-4" />
                  New Chat
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle>Create New Chat Session</DialogTitle>
                  <DialogDescription>
                    Give your new chat session a name to help you organize your conversations.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="name" className="text-right">
                      Name
                    </Label>
                    <Input
                      id="name"
                      value={newSessionName}
                      onChange={(e) => setNewSessionName(e.target.value)}
                      className="col-span-3"
                      placeholder="New Chat Session"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button 
                    onClick={createNewSession} 
                    disabled={isCreating}
                    className="gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    Create Session
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
        
        <p className="text-sm text-muted-foreground">
          Manage your chat conversations and continue where you left off
        </p>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 p-4">
        <div className="mx-auto max-w-4xl">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <MessageCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground animate-pulse" />
                <p className="text-muted-foreground">Loading chat sessions...</p>
              </div>
            </div>
          ) : chatSessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <MessageCircle className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-xl font-semibold mb-2">No chat sessions yet</h3>
              <p className="text-muted-foreground mb-6 max-w-md">
                Start your first conversation to begin building your chat history. 
                Each session will be saved here for easy access.
              </p>
              <Button onClick={() => router.push('/')} className="gap-2">
                <Plus className="h-4 w-4" />
                Start New Chat
              </Button>
            </div>
          ) : (
            <>
              <div className="mb-4 text-sm text-muted-foreground">
                {chatSessions.length} chat session{chatSessions.length !== 1 ? 's' : ''}
              </div>
              
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {chatSessions.map((session) => (
                  <Card key={session.id} className="hover:shadow-md transition-shadow cursor-pointer group">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <CardTitle className="text-base leading-tight mb-2 truncate">
                            {session.session_name}
                          </CardTitle>
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline" className="text-xs">
                              <MessageCircle className="h-3 w-3 mr-1" />
                              Chat Session
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <Calendar className="h-3 w-3" />
                            Created: {formatDate(session.created_at)}
                          </div>
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            Updated: {formatDate(session.updated_at)}
                          </div>
                        </div>
                        
                        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                className="h-8 w-8 p-0"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setEditingSession(session)
                                  setNewSessionName(session.session_name)
                                }}
                              >
                                <Edit2 className="h-3 w-3" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="sm:max-w-[425px]">
                              <DialogHeader>
                                <DialogTitle>Rename Chat Session</DialogTitle>
                                <DialogDescription>
                                  Update the name of your chat session.
                                </DialogDescription>
                              </DialogHeader>
                              <div className="grid gap-4 py-4">
                                <div className="grid grid-cols-4 items-center gap-4">
                                  <Label htmlFor="rename" className="text-right">
                                    Name
                                  </Label>
                                  <Input
                                    id="rename"
                                    value={newSessionName}
                                    onChange={(e) => setNewSessionName(e.target.value)}
                                    className="col-span-3"
                                  />
                                </div>
                              </div>
                              <DialogFooter>
                                <Button 
                                  onClick={() => updateSessionName(editingSession?.id, newSessionName)}
                                  className="gap-2"
                                >
                                  <Edit2 className="h-4 w-4" />
                                  Update Name
                                </Button>
                              </DialogFooter>
                            </DialogContent>
                          </Dialog>

                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Delete Chat Session</AlertDialogTitle>
                                <AlertDialogDescription>
                                  Are you sure you want to delete "{session.session_name}"? 
                                  This action cannot be undone and all messages in this session will be lost.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancel</AlertDialogCancel>
                                <AlertDialogAction 
                                  onClick={() => deleteSession(session.id)}
                                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                >
                                  Delete Session
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent className="pt-0">
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-muted-foreground">
                          ID: #{session.id}
                        </div>
                        <div className="flex gap-2">
                          <Link href={`/chat/${session.id}`}>
                            <Button size="sm" className="h-8 text-xs gap-2">
                              <MessageCircle className="h-3 w-3" />
                              Continue Chat
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}