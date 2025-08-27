"use client"

import * as React from "react"
import { Search, FileText, Calendar, ExternalLink, MessageCircle } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { ScrollArea } from "@/components/ui/scroll-area"

const legalDocuments = [
  {
    id: "1",
    title: "Companies Act No. 07 of 2007",
    category: "Corporate Law",
    date: "2007-05-15",
    summary: "Comprehensive legislation governing company formation, management, and dissolution in Sri Lanka.",
    highlights: ["Company registration procedures", "Director responsibilities", "Shareholder rights"],
    source: "Parliament of Sri Lanka"
  },
  {
    id: "2",
    title: "Consumer Affairs Authority Act No. 09 of 2003",
    category: "Consumer Protection",
    date: "2003-03-20",
    summary: "Establishes the Consumer Affairs Authority and provides protection for consumer rights.",
    highlights: ["Consumer complaint procedures", "Product safety standards", "Fair trading practices"],
    source: "Consumer Affairs Authority"
  }
]

const categories = ["All", "Corporate Law", "Consumer Protection", "Labor Law", "IP Law", "Privacy Law", "Environmental Law"]

export function DiscoverInterface() {
  const [searchQuery, setSearchQuery] = React.useState("")
  const [selectedCategory, setSelectedCategory] = React.useState("All")
  const [urls, setUrls] = React.useState([])
  const [filteredDocuments, setFilteredDocuments] = React.useState([...legalDocuments, ...urls])

  const handleSearch = async () => {
    try{
      const response = await fetch("http://localhost:8000/get_docs/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ query: searchQuery })
      })
      const data = await response.json()
      const docUrls = Object.values(data)
      console.log("Search results:", docUrls)

      setUrls(data || [])

    } catch(error) {
      console.error("Error fetching search results:", error)
    }
  }

  React.useEffect(() => {
    let filtered = [...legalDocuments, ...urls]

    if (selectedCategory !== "All") {
      filtered = filtered.filter(doc => doc.category === selectedCategory)
    }

    if (searchQuery) {
      filtered = filtered.filter(doc =>
        doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.highlights.some(highlight => 
          highlight.toLowerCase().includes(searchQuery.toLowerCase())
        )
      )
    }

    setFilteredDocuments(filtered)
  }, [searchQuery, selectedCategory])

  return (
    <div className="flex h-screen flex-col overflow-y-auto">
      {/* Header */}
      <div className="border-b border-border/40 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <SidebarTrigger />
            <h1 className="text-lg font-semibold">Discover Legal Documents</h1>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex relative mb-4">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search legal documents, acts, and regulations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
          <Button onClick={handleSearch} className="w-32 mx-5 mb-4">Search</Button>
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
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {filteredDocuments.map((document) => (
              <Card key={document.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-base leading-tight mb-2">
                        {document.title}
                      </CardTitle>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="secondary" className="text-xs">
                          {document.category}
                        </Badge>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Calendar className="h-3 w-3" />
                          {new Date(document.date).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                  <CardDescription className="text-sm">
                    {document.summary}
                  </CardDescription>
                </CardHeader>

                <CardContent className="pt-0">
                  <div className="mb-4">
                    <div className="text-xs font-medium text-muted-foreground mb-2">
                      Key Highlights:
                    </div>
                    <ul className="space-y-1">
                      {document.highlights.map((highlight, index) => (
                        <li key={index} className="text-xs text-muted-foreground flex items-start gap-1">
                          <span className="text-primary">•</span>
                          {highlight}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-xs text-muted-foreground">
                      Source: {document.source}
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" className="h-8 text-xs">
                        <MessageCircle className="h-3 w-3 mr-1" />
                        Ask AI
                      </Button>
                      <Button size="sm" variant="outline" className="h-8 text-xs">
                        <ExternalLink className="h-3 w-3 mr-1" />
                        View
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          {Array.isArray(urls) && urls.length > 0 && (
            <div className="mt-8 max-w-4xl mx-auto">
              <h2 className="text-xl font-semibold mb-6 text-foreground">Related Documents</h2>
              <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-2">
                {urls.map((url, index) => (
                  <Card key={index} className="overflow-hidden hover:shadow-lg transition-shadow duration-200">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium text-muted-foreground">
                          Document {index + 1}
                        </CardTitle>
                        <Badge variant="outline" className="text-xs">
                          PDF
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="p-0">
                      <div className="relative group">
                        <iframe 
                          src={`https://docs.google.com/gview?url=${url}&embedded=true`}
                          className="w-full h-64 border-0 rounded-b-lg"
                          title={`Document ${index + 1}`}
                          loading="lazy"
                        />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-200 rounded-b-lg" />
                      </div>
                      <div className="p-4 bg-muted/30">
                        <div className="flex items-center justify-between">
                          <p className="text-xs text-muted-foreground truncate flex-1 mr-3">
                            {url}
                          </p>
                          <div className="flex gap-2">
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="h-7 text-xs"
                              onClick={() => window.open(url, '_blank')}
                            >
                              <ExternalLink className="h-3 w-3 mr-1" />
                              Open
                            </Button>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}
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
