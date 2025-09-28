"use client"

import * as React from "react"
import { MessageCircle, FileText, Clock, Search, Filter, MoreHorizontal, Trash2, BookOpen, Eye, ExternalLink, Calendar } from 'lucide-react'
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { useAuth } from "@/contexts/AuthContext"
import Link from "next/link"

const historyItems = [
  {
    id: "1",
    type: "chat",
    title: "Business Registration Requirements",
    summary: "Discussed the process of registering a new business in Sri Lanka, including required documents and fees.",
    timestamp: new Date(Date.now() - 86400000), // 1 day ago
    category: "Corporate Law",
    messageCount: 12
  },
  {
    id: "2",
    type: "document",
    title: "Companies Act No. 07 of 2007",
    summary: "Reviewed sections related to director responsibilities and company governance.",
    timestamp: new Date(Date.now() - 172800000), // 2 days ago
    category: "Corporate Law",
    documentType: "Act"
  },
  {
    id: "3",
    type: "chat",
    title: "Employment Contract Clauses",
    summary: "Asked about mandatory clauses in employment contracts and termination procedures.",
    timestamp: new Date(Date.now() - 259200000), // 3 days ago
    category: "Labor Law",
    messageCount: 8
  }
]

const categories = ["All", "Corporate Law", "Labor Law", "Consumer Law", "IP Law", "Tax Law"]
const timeFilters = ["All Time", "Today", "This Week", "This Month", "Last 3 Months"]

export function HistoryInterface() {
  const { token, logout } = useAuth()
  const [searchQuery, setSearchQuery] = React.useState("")
  const [selectedCategory, setSelectedCategory] = React.useState("All")
  const [selectedTimeFilter, setSelectedTimeFilter] = React.useState("All Time")
  const [recentDocuments, setRecentDocuments] = React.useState([])
  const [recentChats, setRecentChats] = React.useState([])
  const [isLoading, setIsLoading] = React.useState(true)

  // Fetch recent chat sessions
  React.useEffect(() => {
    const fetchRecentChats = async () => {
      if (!token) {
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
          logout()
          return
        }

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        // Get the 3 most recent chat sessions
        const recent = (data || []).slice(0, 3).map(chat => ({
          id: `chat-${chat.id}`,
          type: "chat",
          title: chat.session_name,
          summary: "Continue your legal conversation and get personalized insights.",
          timestamp: new Date(chat.updated_at),
          category: "Chat Session",
          chatId: chat.id,
          created: new Date(chat.created_at)
        }))
        setRecentChats(recent)
        
      } catch (error) {
        console.error('Error fetching recent chats:', error)
        setRecentChats([])
      }
    }
    
    fetchRecentChats()
  }, [token, logout])

  // Load recently viewed documents from localStorage
  React.useEffect(() => {
    const loadRecentDocuments = () => {
      try {
        const stored = localStorage.getItem('recentlyViewedDocuments')
        if (stored) {
          const parsed = JSON.parse(stored)
          // Get the 5 most recent documents
          const recent = parsed.slice(0, 5).map((doc, index) => ({
            id: `doc-${index}`,
            type: "document",
            title: doc.title || 'Legal Document',
            summary: doc.summary || 'Recently viewed legal document',
            timestamp: new Date(doc.viewedAt),
            category: doc.category || 'Legal Documents',
            url: doc.url,
            source: doc.source || 'documents.gov.lk'
          }))
          setRecentDocuments(recent)
        }
      } catch (error) {
        console.error('Error loading recent documents:', error)
        setRecentDocuments([])
      } finally {
        setIsLoading(false)
      }
    }

    loadRecentDocuments()
  }, [])

  // Combine recent items
  const allRecentItems = React.useMemo(() => {
    const combined = [...recentChats, ...recentDocuments]
    return combined.sort((a, b) => b.timestamp - a.timestamp)
  }, [recentChats, recentDocuments])

  // Apply filters
  const filteredItems = React.useMemo(() => {
    let filtered = allRecentItems

    if (selectedCategory !== "All") {
      filtered = filtered.filter(item => item.category === selectedCategory)
    }

    if (searchQuery) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.summary.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    // Apply time filter
    if (selectedTimeFilter !== "All Time") {
      const now = new Date()
      const filterDate = new Date()
      
      switch (selectedTimeFilter) {
        case "Today":
          filterDate.setHours(0, 0, 0, 0)
          break
        case "This Week":
          filterDate.setDate(now.getDate() - 7)
          break
        case "This Month":
          filterDate.setMonth(now.getMonth() - 1)
          break
        case "Last 3 Months":
          filterDate.setMonth(now.getMonth() - 3)
          break
      }
      
      filtered = filtered.filter(item => item.timestamp >= filterDate)
    }

    return filtered
  }, [allRecentItems, searchQuery, selectedCategory, selectedTimeFilter])

  // Create categories based on available data
  const availableCategories = React.useMemo(() => {
    const categories = new Set(["All"])
    allRecentItems.forEach(item => categories.add(item.category))
    return Array.from(categories)
  }, [allRecentItems])

  const formatTimestamp = (timestamp) => {
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - timestamp.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) {
      return "Just now"
    } else if (diffInHours < 24) {
      return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`
    } else if (diffInHours < 168) { // 7 days
      const days = Math.floor(diffInHours / 24)
      return `${days} day${days > 1 ? 's' : ''} ago`
    } else {
      return timestamp.toLocaleDateString()
    }
  }

  const handleDocumentView = (document) => {
    // Track document view
    const viewedDoc = {
      title: document.title,
      summary: document.summary,
      category: document.category,
      url: document.url,
      source: document.source,
      viewedAt: new Date().toISOString()
    }

    try {
      const stored = localStorage.getItem('recentlyViewedDocuments')
      const recent = stored ? JSON.parse(stored) : []
      
      // Remove if already exists and add to front
      const filtered = recent.filter(doc => doc.url !== viewedDoc.url)
      const updated = [viewedDoc, ...filtered].slice(0, 10) // Keep only 10 most recent
      
      localStorage.setItem('recentlyViewedDocuments', JSON.stringify(updated))
    } catch (error) {
      console.error('Error saving viewed document:', error)
    }

    // Open document
    if (document.url) {
      window.open(document.url, '_blank')
    }
  }

  return (
    <div className="flex h-screen flex-col overflow-y-auto">
      {/* Header */}
      <div className="border-b border-border/40 p-4">
        <div className="flex items-center gap-2 mb-4">
          <SidebarTrigger />
          <h1 className="text-lg font-semibold">Recent Activity</h1>
        </div>
        <p className="text-sm text-muted-foreground mb-4">
          Recently viewed documents and chat sessions
        </p>

        {/* Search and Filters */}
        <div className="space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search your recent activity..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <div className="flex flex-wrap gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="text-xs">
                  <Filter className="h-3 w-3 mr-1" />
                  {selectedCategory}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {availableCategories.map((category) => (
                  <DropdownMenuItem
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                  >
                    {category}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="text-xs">
                  <Clock className="h-3 w-3 mr-1" />
                  {selectedTimeFilter}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {timeFilters.map((filter) => (
                  <DropdownMenuItem
                    key={filter}
                    onClick={() => setSelectedTimeFilter(filter)}
                  >
                    {filter}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 p-4">
        <div className="mx-auto max-w-4xl">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Clock className="h-12 w-12 mx-auto mb-4 text-muted-foreground animate-pulse" />
                <p className="text-muted-foreground">Loading recent activity...</p>
              </div>
            </div>
          ) : (
            <>
              <div className="mb-4 text-sm text-muted-foreground">
                Showing {filteredItems.length} recent items
              </div>

              <div className="space-y-4">
                {filteredItems.map((item) => (
                  <Card key={item.id} className="hover:shadow-md transition-shadow group">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3 flex-1">
                          <div className="mt-1">
                            {item.type === "chat" ? (
                              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                                <MessageCircle className="h-5 w-5 text-primary" />
                              </div>
                            ) : (
                              <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center group-hover:bg-blue-100 transition-colors">
                                <FileText className="h-5 w-5 text-blue-600" />
                              </div>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <CardTitle className="text-base leading-tight mb-2 truncate">
                              {item.title}
                            </CardTitle>
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                              <Badge variant="outline" className="text-xs">
                                {item.category}
                              </Badge>
                              {item.type === "chat" && (
                                <Badge variant="secondary" className="text-xs bg-green-50 text-green-700 border-green-200">
                                  Chat Session
                                </Badge>
                              )}
                              {item.type === "document" && (
                                <Badge variant="secondary" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                                  Document
                                </Badge>
                              )}
                              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                                <Clock className="h-3 w-3" />
                                {formatTimestamp(item.timestamp)}
                              </div>
                            </div>
                            <CardDescription className="text-sm">
                              {item.summary}
                            </CardDescription>
                          </div>
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent className="pt-0">
                      <div className="flex justify-between items-center">
                        <div className="text-xs text-muted-foreground">
                          {item.type === "chat" ? (
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              Created: {item.created ? formatTimestamp(item.created) : 'Recently'}
                            </span>
                          ) : (
                            <span className="flex items-center gap-1">
                              <ExternalLink className="h-3 w-3" />
                              Source: {item.source}
                            </span>
                          )}
                        </div>
                        <div className="flex gap-2">
                          {item.type === "chat" ? (
                            <>
                              <Link href={`/chat/${item.chatId}`}>
                                <Button size="sm" variant="outline" className="h-8 text-xs">
                                  <Eye className="h-3 w-3 mr-1" />
                                  View
                                </Button>
                              </Link>
                              <Link href={`/chat/${item.chatId}`}>
                                <Button size="sm" className="h-8 text-xs">
                                  <MessageCircle className="h-3 w-3 mr-1" />
                                  Continue
                                </Button>
                              </Link>
                            </>
                          ) : (
                            <>
                              <Button 
                                size="sm" 
                                variant="outline" 
                                className="h-8 text-xs"
                                onClick={() => {
                                  // Store document context for Ask AI feature
                                  const documentContext = `Document: ${item.title}\nCategory: ${item.category}\nSummary: ${item.summary}`
                                  localStorage.setItem('chatContext', JSON.stringify({
                                    document: item,
                                    initialQuery: `I have a question about "${item.title}". `,
                                    documentContext: documentContext
                                  }))
                                  window.location.href = '/'
                                }}
                              >
                                <MessageCircle className="h-3 w-3 mr-1" />
                                Ask AI
                              </Button>
                              <Button 
                                size="sm" 
                                className="h-8 text-xs"
                                onClick={() => handleDocumentView(item)}
                              >
                                <ExternalLink className="h-3 w-3 mr-1" />
                                View Again
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {filteredItems.length === 0 && (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  {allRecentItems.length === 0 ? (
                    <>
                      <Clock className="h-16 w-16 text-muted-foreground mb-4" />
                      <h3 className="text-xl font-semibold mb-2">No Recent Activity</h3>
                      <p className="text-muted-foreground mb-6 max-w-md">
                        Start exploring documents or chatting to see your recent activity here.
                      </p>
                      <div className="flex gap-3">
                        <Link href="/">
                          <Button className="gap-2">
                            <MessageCircle className="h-4 w-4" />
                            Start Chat
                          </Button>
                        </Link>
                        <Link href="/discover">
                          <Button variant="outline" className="gap-2">
                            <FileText className="h-4 w-4" />
                            Discover Documents
                          </Button>
                        </Link>
                      </div>
                    </>
                  ) : (
                    <>
                      <Search className="h-12 w-12 text-muted-foreground mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No items found</h3>
                      <p className="text-muted-foreground">
                        Try adjusting your search terms or filters
                      </p>
                    </>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
