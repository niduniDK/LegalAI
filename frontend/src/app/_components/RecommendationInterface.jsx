"use client"

import * as React from "react"
import { Star, MessageCircle, FileText, Clock, ExternalLink } from 'lucide-react';
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import Link from "next/link"
import { useAuth } from "@/contexts/AuthContext"

const recommendations = [
  // {
  //   id: "1",
  //   title: "Business Registration Requirements",
  //   category: "Corporate Law",
  //   relevanceScore: 95,
  //   reason: "Based on your recent queries about starting a business",
  //   summary: "Complete guide to registering a business in Sri Lanka, including required documents and procedures.",
  //   estimatedReadTime: "8 min",
  //   lastUpdated: "2024-01-15",
  //   tags: ["Business", "Registration", "Startup"],
  //   actionType: "document" 
  // },
  // {
  //   id: "2",
  //   title: "Employment Contract Templates",
  //   category: "Labor Law",
  //   relevanceScore: 88,
  //   reason: "Frequently accessed by users with similar interests",
  //   summary: "Standard employment contract templates compliant with Sri Lankan labor laws.",
  //   estimatedReadTime: "12 min",
  //   lastUpdated: "2024-02-01",
  //   tags: ["Employment", "Contracts", "HR"],
  //   actionType: "document" 
  // }
]

export function RecommendationsInterface() {
  const { token, logout } = useAuth()
  const [userRecommendations, setUserRecommendations] = React.useState([])
  const [user, setUser] = React.useState(null)
  const [preferences, setPreferences] = React.useState([])
  const [loading, setLoading] = React.useState(false)
  const [language, setLanguage] = React.useState("en")

  // Fetch user data and set username
  React.useEffect(() => {
    const fetchUserData = async () => {
      if (!token) return
      
      try {
        const response = await fetch("http://localhost:8000/auth/me", {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          setUser(data)
          localStorage.setItem('username', data.first_name || data.username || '')
        }
      } catch(error){
        console.error("Error fetching user data:", error);
      }
    }

    fetchUserData()
  }, [token])

  // Fetch preferences
  const fetchPreferences = async () => {
    if (!token) return []
    
    try {
      const response = await fetch("http://localhost:8000/auth/preferences", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        const userPreferences = data.preference_value || []
        setPreferences(userPreferences)
        return userPreferences
      }
    } catch(error) {
      console.error("Error fetching preferences:", error);
    }
    return []
  }

  // Fetch document recommendations
  const fetchRecommendations = async (username, userPreferences) => {
    if (!username) return
    
    try {
      setLoading(true)
      const response = await fetch("http://localhost:8000/recommendations/get_recommendations/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username: username, 
          preferences: userPreferences,
          language: language
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log("Recommendations response:", data)
        const urls = Object.values(data)
        setUserRecommendations(urls)
      }
    } catch(error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false)
    }
  }

  // Main effect to coordinate data fetching
  React.useEffect(() => {
    const loadRecommendations = async () => {
      if (!token) return
      
      // First fetch preferences
      const userPreferences = await fetchPreferences()
      
      // Get username from localStorage (set by user data fetch)
      const username = localStorage.getItem('username')
      
      // Fetch recommendations with both username and preferences
      if (username) {
        await fetchRecommendations(username, userPreferences)
      }
    }

    // Add a small delay to ensure user data is fetched first
    const timer = setTimeout(loadRecommendations, 100)
    return () => clearTimeout(timer)
  }, [token, user, language])

  return (
    <div className="flex h-screen flex-col overflow-y-auto">
      {/* Header */}
      <div className="border-b border-border/40 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-semibold">Personalized Recommendations</h1>
          </div>
          <div className="flex items-center gap-2">
            <select 
              className="text-sm border border-border rounded-md px-2 py-1 bg-background text-foreground hover:bg-muted/50 transition-colors"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="si">සිංහල</option>
              <option value="ta">தமිழ්</option>
            </select>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          Curated legal content based on your interests and recent activity
        </p>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="mx-auto max-w-4xl space-y-6">
          {/* Recommendations */}
          <div>
            <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
              <Star className="h-4 w-4" />
              Recommended for You
            </h2>
            
            {loading ? (
              <div className="grid gap-4 md:grid-cols-2">
                {[1, 2, 3, 4].map((i) => (
                  <Card key={i} className="animate-pulse">
                    <CardHeader className="pb-3">
                      <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
                      <div className="h-3 bg-muted rounded w-1/2 mb-2"></div>
                      <div className="h-3 bg-muted rounded w-full"></div>
                    </CardHeader>
                    <CardContent>
                      <div className="h-20 bg-muted rounded"></div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : userRecommendations.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2">
                {userRecommendations.map((url, index) => {
                  // Extract document information from URL (same logic as DiscoverInterface)
                  let docType = "Document"
                  let filename = ""
                  let category = "General"
                  let extractedDate = new Date().toISOString().split('T')[0] // Default to today
                  
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

                  const document = {
                    id: `rec-${index}`,
                    title: filename || `${docType} Document ${index + 1}`,
                    category: category,
                    date: extractedDate,
                    summary: `Recommended ${docType.toLowerCase()} document based on your interests and recent activity`,
                    highlights: [
                      "Personalized recommendation",
                      "Government document",
                      "PDF format available"
                    ],
                    source: "documents.gov.lk",
                    url: url
                  }

                  const handleAskAI = (doc) => {
                    // Create a query about the document
                    const documentContext = `Document: ${doc.title}\nCategory: ${doc.category}\nSummary: ${doc.summary}`
                    const query = `I have a question about "${doc.title}". `
                    
                    // Store the document context and query in localStorage for the chat interface
                    localStorage.setItem('chatContext', JSON.stringify({
                      document: doc,
                      initialQuery: query,
                      documentContext: documentContext
                    }))
                    
                    // Navigate to chat interface
                    window.location.href = '/'
                  }

                  return (
                    <Card key={index} className="hover:shadow-md transition-shadow">
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
                                <Clock className="h-3 w-3" />
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
                            {document.highlights.map((highlight, idx) => (
                              <li key={idx} className="text-xs text-muted-foreground flex items-start gap-1">
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
                              onClick={() => window.open(url, '_blank')}
                            >
                              <ExternalLink className="h-3 w-3 mr-1" />
                              View
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            ) : (
              <Card className="p-6 text-center">
                <Star className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">No Recommendations Yet</h3>
                <p className="text-muted-foreground mb-4">
                  We're learning your preferences to provide personalized recommendations.
                </p>
                <Link href="/discover">
                  <Button className="gap-2">
                    <FileText className="h-4 w-4" />
                    Browse Documents
                  </Button>
                </Link>
              </Card>
            )}
            
            <div className="space-y-4 mt-6">
              {recommendations.map((rec) => (
                <Card key={rec.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <CardTitle className="text-base leading-tight">
                            {rec.title}
                          </CardTitle>
                          <div className="flex items-center gap-1">
                            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                            <span className="text-xs text-muted-foreground">
                              {rec.relevanceScore}% match
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant="outline" className="text-xs">
                            {rec.category}
                          </Badge>
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Clock className="h-3 w-3" />
                            {rec.estimatedReadTime}
                          </div>
                        </div>
                      </div>
                    </div>
                    <CardDescription className="text-sm mb-2">
                      {rec.summary}
                    </CardDescription>
                    <div className="text-xs text-muted-foreground italic">
                      {rec.reason}
                    </div>
                  </CardHeader>

                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between">
                      <div className="flex flex-wrap gap-1">
                        {rec.tags.map((tag, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      <div className="flex gap-2">
                        {rec.actionType === "chat" ? (
                          <Link to="/">
                            <Button size="sm" className="h-8 text-xs">
                              <MessageCircle className="h-3 w-3 mr-1" />
                              Start Chat
                            </Button>
                          </Link>
                          
                        ) : (
                          <Button size="sm" variant="outline" className="h-8 text-xs">
                            <FileText className="h-3 w-3 mr-1" />
                            View Document
                          </Button>
                        )}
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-muted-foreground">
                      Last updated: {new Date(rec.lastUpdated).toLocaleDateString()}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div>
            <h2 className="text-base font-semibold mb-4">Quick Actions</h2>
            <div className="grid gap-3 md:grid-cols-3">
              <Link href="/">
              <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow">
                <div className="text-center">
                  <MessageCircle className="h-8 w-8 mx-auto mb-2 text-primary" />
                  <h3 className="font-medium text-sm mb-1">Ask Legal Question</h3>
                  <p className="text-xs text-muted-foreground">Get instant answers from our AI</p>
                </div>
              </Card>
              </Link>
              <Link href='/discover'>
                <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow">
                  <div className="text-center">
                    <FileText className="h-8 w-8 mx-auto mb-2 text-primary" />
                    <h3 className="font-medium text-sm mb-1">Browse Documents</h3>
                    <p className="text-xs text-muted-foreground">Explore legal documents and acts</p>
                  </div>
                </Card>
              </Link>
              
              <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow">
                <div className="text-center">
                  <Star className="h-8 w-8 mx-auto mb-2 text-primary" />
                  <h3 className="font-medium text-sm mb-1">Save Favorites</h3>
                  <p className="text-xs text-muted-foreground">Bookmark important resources</p>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
