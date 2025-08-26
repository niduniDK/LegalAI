"use client"

import * as React from "react"
import { MessageCircle, FileText, Clock, Search, Filter, MoreHorizontal, Trash2, BookOpen } from 'lucide-react'
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
  const [searchQuery, setSearchQuery] = React.useState("")
  const [selectedCategory, setSelectedCategory] = React.useState("All")
  const [selectedTimeFilter, setSelectedTimeFilter] = React.useState("All Time")
  const [filteredItems, setFilteredItems] = React.useState(historyItems)

  React.useEffect(() => {
    let filtered = historyItems

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

    setFilteredItems(filtered)
  }, [searchQuery, selectedCategory, selectedTimeFilter])

  const formatTimestamp = (timestamp) => {
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - timestamp.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 24) {
      return `${diffInHours} hours ago`
    } else if (diffInHours < 168) { // 7 days
      return `${Math.floor(diffInHours / 24)} days ago`
    } else {
      return timestamp.toLocaleDateString()
    }
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <div className="border-b border-border/40 p-4">
        <div className="flex items-center gap-2 mb-4">
          <SidebarTrigger />
          <h1 className="text-lg font-semibold">History & Past Conversations</h1>
        </div>

        {/* Search and Filters */}
        <div className="space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search your history..."
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
                {categories.map((category) => (
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
          <div className="mb-4 text-sm text-muted-foreground">
            Showing {filteredItems.length} items
          </div>

          <div className="space-y-4">
            {filteredItems.map((item) => (
              <Card key={item.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="mt-1">
                        {item.type === "chat" ? (
                          <MessageCircle className="h-4 w-4 text-primary" />
                        ) : (
                          <FileText className="h-4 w-4 text-primary" />
                        )}
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-base leading-tight mb-2">
                          {item.title}
                        </CardTitle>
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant="outline" className="text-xs">
                            {item.category}
                          </Badge>
                          {item.type === "chat" && item.messageCount && (
                            <Badge variant="secondary" className="text-xs">
                              {item.messageCount} messages
                            </Badge>
                          )}
                          {item.type === "document" && item.documentType && (
                            <Badge variant="secondary" className="text-xs">
                              {item.documentType}
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
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem>
                          <BookOpen className="h-4 w-4 mr-2" />
                          {item.type === "chat" ? "Continue Chat" : "Open Document"}
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive">
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </CardHeader>

                <CardContent className="pt-0">
                  <div className="flex justify-between items-center">
                    <div className="text-xs text-muted-foreground">
                      {item.type === "chat" ? "Conversation" : "Document Access"}
                    </div>
                    <Button size="sm" variant="outline" className="h-8 text-xs">
                      {item.type === "chat" ? "Resume Chat" : "View Again"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredItems.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Clock className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No history found</h3>
              <p className="text-muted-foreground">
                {searchQuery || selectedCategory !== "All" || selectedTimeFilter !== "All Time"
                  ? "Try adjusting your search or filters"
                  : "Start a conversation to see your history here"}
              </p>
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  )
}
