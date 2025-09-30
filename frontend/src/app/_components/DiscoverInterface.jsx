"use client"

import * as React from "react"
import { Search, FileText, Calendar, ExternalLink, MessageCircle } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useAuth } from "@/contexts/AuthContext"

const legalDocuments = [
  // {
  //   id: "1",
  //   title: "Companies Act No. 07 of 2007",
  //   category: "Corporate Law",
  //   date: "2007-05-15",
  //   summary: "Comprehensive legislation governing company formation, management, and dissolution in Sri Lanka.",
  //   highlights: ["Company registration procedures", "Director responsibilities", "Shareholder rights"],
  //   source: "Parliament of Sri Lanka"
  // },
  // {
  //   id: "2",
  //   title: "Consumer Affairs Authority Act No. 09 of 2003",
  //   category: "Consumer Protection",
  //   date: "2003-03-20",
  //   summary: "Establishes the Consumer Affairs Authority and provides protection for consumer rights.",
  //   highlights: ["Consumer complaint procedures", "Product safety standards", "Fair trading practices"],
  //   source: "Consumer Affairs Authority"
  // }
]

const categories = ["All", "Corporate Law", "Consumer Protection", "Labor Law", "IP Law", "Privacy Law", "Environmental Law", "Bills", "Acts", "Gazettes", "Constitution", "Legal Documents"]

export function DiscoverInterface() {
  const { token, user, logout } = useAuth()
  const [searchQuery, setSearchQuery] = React.useState("")
  const [selectedCategory, setSelectedCategory] = React.useState("All")
  const [urls, setUrls] = React.useState([])
  const [filteredDocuments, setFilteredDocuments] = React.useState([])
  const [language, setLanguage] = React.useState("en")

  let i = 0;

  const updateHistory = async () => {
    if (!token) {
      console.warn("No authentication token available")
      return
    }

    // Debug token information
    console.log("Token being used:", token ? `${token.substring(0, 20)}...` : "No token")
    console.log("Token type:", typeof token)
    console.log("Token length:", token?.length)
    console.log("User data:", user)

    // Generate a unique preference key
    const preferenceKey = "search"

    try {
      const response = await fetch("http://localhost:8000/get_docs/preferences", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ 
          preference_key: preferenceKey,
          preference_value: searchQuery
        })
      })
      
      console.log("Response status:", response.status)
      console.log("Response headers:", Object.fromEntries(response.headers.entries()))
      
      if (response.status === 401) {
        console.error("Token expired or invalid. Please log in again.")
        const errorResponse = await response.text()
        console.error("401 Error details:", errorResponse)
        
        // Automatically log out user when token expires
        if (logout) {
          logout()
          alert("Your session has expired. Please log in again.")
        }
        return
      }
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error("Error response body:", errorText)
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`)
      }
      
      const data = await response.json()
      console.log("History updated successfully:", data)
      
    } catch (error) {
      console.error("Error updating history:", error)
      // Show user-friendly error message
      if (error.message.includes('401')) {
        console.error("Authentication failed. Please log in again.")
      }
    }
  }

  const handleSearch = async () => {
    try {
      const response = await fetch("http://localhost:8000/get_docs/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { "Authorization": `Bearer ${token}` })
        },
        body: JSON.stringify({ query: searchQuery, language: language })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log("Search results:", data)
      
      // Update history only if user is authenticated
      if (token) {
        await updateHistory()
      }

      setUrls(data || [])
      
      // Reset category filter to "All" when showing search results
      if (data && data.length > 0) {
        setSelectedCategory("All")
        setFilteredDocuments(data)
      }

    } catch (error) {
      console.error("Error fetching search results:", error)
    }
  }

  const handleAskAI = (document) => {
    // Track document view
    trackDocumentView(document)
    
    // Create a query about the document
    const documentContext = `Document: ${document.title}\nCategory: ${document.category}\nSummary: ${document.summary}`
    const query = `I have a question about "${document.title}". `
    
    // Store the document context and query in localStorage for the chat interface
    localStorage.setItem('chatContext', JSON.stringify({
      document: document,
      initialQuery: query,
      documentContext: documentContext
    }))
    
    // Navigate to chat interface - assuming it's at /chat route
    // You might need to adjust this based on your routing structure
    window.location.href = '/'
  }

  const handleViewDocument = (document) => {
    // Track document view
    trackDocumentView(document)
    
    // Open document in new tab
    if (document.url) {
      window.open(document.url, '_blank')
    }
  }

  const trackDocumentView = (document) => {
    const viewedDoc = {
      title: document.title,
      summary: document.summary,
      category: document.category,
      url: document.url,
      source: document.source || 'documents.gov.lk',
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
      console.error('Error tracking document view:', error)
    }
  }

  React.useEffect(() => {
    console.log("URLs state:", urls)
    console.log("URLs length:", urls.length)
    console.log("URLs type:", typeof urls[0])
    
    // Convert URLs or document objects to proper document objects
    const urlDocuments = urls.map((item, index) => {
      // If it's already a document object, use it as-is
      if (typeof item === 'object' && item !== null && item.title) {
        return {
          ...item,
          id: item.id || `doc-${index}`,
          isSearchResult: true
        }
      }
      
      // If it's a URL string, convert it to a document object
      let docType = "Document"
      let filename = ""
      let category = "General"
      let extractedDate = new Date().toISOString().split('T')[0] // Default to today
      let url = typeof item === 'string' ? item : item.url || ''
      
      const basePath = "https://documents.gov.lk/view/"
      if (url.startsWith(basePath)) {
        const afterBase = url.slice(basePath.length)
        const parts = afterBase.split("/")
        if (parts.length > 1) {
          docType = parts[0]
          
          // Extract date from URL structure: /type/year/month/day-filename.pdf
          if (parts.length >= 4) {
            const year = parts[1]
            const month = parts[2]
            const dayAndFile = parts[3]
            
            // Extract day from the filename (before the first dash or underscore)
            const dayMatch = dayAndFile.match(/^(\d{1,2})/)
            const day = dayMatch ? dayMatch[1].padStart(2, '0') : '01'
            
            // Validate and construct date
            if (year.match(/^\d{4}$/) && month.match(/^\d{1,2}$/) && day.match(/^\d{1,2}$/)) {
              const paddedMonth = month.padStart(2, '0')
              extractedDate = `${year}-${paddedMonth}-${day}`
            }
          }
          
          // Get filename (last part of the path)
          filename = parts.slice(1).join("/")
          
          // Set category based on document type
          switch(docType.toLowerCase()) {
            case 'bills':
              category = "Bills"
              break
            case 'acts':
              category = "Acts"
              break
            case 'gazettes':
              category = "Gazettes"
              break
            case 'constitution':
              category = "Constitution"
              break
            default:
              category = "Legal Documents"
          }
        }
      }
      
      return {
        id: `url-${index}`,
        title: filename || `${docType} Document ${index + 1}`,
        category: category,
        date: extractedDate,
        summary: `Official ${docType.toLowerCase()} document from Sri Lankan government portal`,
        highlights: [
          "Government document",
          "Official publication", 
          "PDF format available"
        ],
        source: "documents.gov.lk",
        url: url,
        isSearchResult: true
      }
    })

    console.log("URL Documents:", urlDocuments)
    
    let filtered = [...legalDocuments, ...urlDocuments]
    console.log("Combined documents:", filtered)
    console.log("Selected category:", selectedCategory)

    if (selectedCategory !== "All") {
      console.log("Filtering by category:", selectedCategory)
      const beforeCategoryFilter = filtered.length
      filtered = filtered.filter(doc => {
        console.log(`Document "${doc.title}" has category "${doc.category}", matches: ${doc.category === selectedCategory}`)
        return doc.category === selectedCategory
      })
      console.log(`Category filtering: ${beforeCategoryFilter} -> ${filtered.length}`)
    }

    // Only apply search query filtering if there are no search results from the API
    // If we have search results from the API, show them all since they're already relevant
    if (searchQuery && urlDocuments.length === 0) {
      console.log("Applying search query filtering")
      filtered = filtered.filter(doc =>
        (doc.title && doc.title.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (doc.summary && doc.summary.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (doc.highlights && doc.highlights.some(highlight => 
          highlight && highlight.toLowerCase().includes(searchQuery.toLowerCase())
        ))
      )
    }

    console.log("Filtered documents:", filtered)
    setFilteredDocuments(filtered)
  }, [searchQuery, selectedCategory, urls])

  return (
    <div className="flex h-screen flex-col overflow-y-auto">
      {/* Header */}
      <div className="border-b border-border/40 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <SidebarTrigger />
            <h1 className="text-lg font-semibold">Discover Legal Documents</h1>
          </div>
          <div className="flex items-center gap-2">
            <select 
              className="text-sm border border-border rounded-md px-2 py-1 bg-background text-foreground hover:bg-muted/50 transition-colors"
              defaultValue="en"
              onClick={(e) => setLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="si">සිංහල</option>
              <option value="ta">தமிழ்</option>
            </select>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex items-center gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search legal documents, acts, and regulations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  handleSearch()
                }
              }}
            />
          </div>
          <Button onClick={handleSearch} className="w-32">Search</Button>
        </div>

        

        {/* Category Filters */}
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category)}
              className="text-xs"
            >
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="flex-1 p-4">
        <div className="mx-auto max-w-4xl">
          <div className="mb-4 text-sm text-muted-foreground">
            Showing {filteredDocuments.length} documents
            {urls.length > 0 && ` (${filteredDocuments.filter(doc => doc.isSearchResult).length} from search results)`}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {filteredDocuments.map((document) => (
              <Card key={document.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-base leading-tight mb-2">
                        {document.title || 'Untitled Document'}
                      </CardTitle>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="secondary" className="text-xs">
                          {document.category || 'General'}
                        </Badge>
                        {document.date && (
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Calendar className="h-3 w-3" />
                            {new Date(document.date).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <CardDescription className="text-sm">
                    {document.summary || 'No description available'}
                  </CardDescription>
                </CardHeader>

                <CardContent className="pt-0">
                  <div className="mb-4">
                    <div className="text-xs font-medium text-muted-foreground mb-2">
                      Key Highlights:
                    </div>
                    <ul className="space-y-1">
                      {(document.highlights || []).map((highlight, index) => (
                        <li key={`${document.id}-hl-${index}`} className="text-xs text-muted-foreground flex items-start gap-1">
                          <span className="text-primary">•</span>
                          {highlight}
                        </li>
                      ))}

                      {(!document.highlights || document.highlights.length === 0) && (
                        <li className="text-xs text-muted-foreground">
                          No highlights available
                        </li>
                      )}
                    </ul>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-xs text-muted-foreground">
                      Source: {document.source || 'Unknown'}
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="h-8 text-xs"
                        onClick={() => handleAskAI(document)}
                      >
                        <MessageCircle className="h-3 w-3 mr-1" />
                        Ask AI
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="h-8 text-xs"
                        onClick={() => handleViewDocument(document)}
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        View
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          {filteredDocuments.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FileText className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No documents found</h3>
              <p className="text-muted-foreground">
                Try adjusting your search terms or category filters
              </p>
            </div>
          )}
        </div>

        
      </ScrollArea>
    </div>
  )
}
