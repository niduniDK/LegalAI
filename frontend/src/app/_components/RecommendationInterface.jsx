"use client"

import * as React from "react"
import { Star, MessageCircle, FileText, Clock, ExternalLink, Eye, Calendar } from 'lucide-react';
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
  const [userRecommendation, setUserRecommendations] = React.useState([])
  const [recommendedChats, setRecommendedChats] = React.useState([])

  React.useEffect(() => {
    localStorage.setItem('username', 'user_2');
  }, []);
  
  // Fetch document recommendations
  React.useEffect(()=> {
    const username = localStorage.getItem('username');
    if(username){
      const fetchRecommendations = async () => {
        try{
          const response = await fetch("http://localhost:8000/recommendations/get_recommendations/", {
            method: "POST",
            headers:{
              "Content-Type": "application/json"
            },
            body: JSON.stringify({username: username})
          })
          const data = await response.json()
          const urls = Object.values(data)
          setUserRecommendations(urls)
        }
        catch(error){
          console.error("Error fetching recommendations:", error);
        }
      }
      fetchRecommendations();
    }
  }, []);

  // Fetch recommended chat sessions
  React.useEffect(() => {
    const fetchRecommendedChats = async () => {
      if (!token) {
        console.warn("No authentication token available for chat recommendations")
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
        console.log("Fetched chat sessions for recommendations:", data)
        
        // Get the 3 most recent chat sessions as recommendations
        const recentChats = (data || []).slice(0, 3)
        setRecommendedChats(recentChats)
        
      } catch (error) {
        console.error('Error fetching recommended chat sessions:', error)
      }
    }
    
    fetchRecommendedChats()
  }, [token, logout])

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


  return (
    <div className="flex h-screen flex-col overflow-y-auto">
      {/* Header */}
      <div className="border-b border-border/40 p-4">
        <div className="flex items-center gap-2 mb-4">
          <h1 className="text-lg font-semibold">Personalized Recommendations</h1>
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
            <div className="grid gap-4 md:grid-cols-2">
              {userRecommendation.length > 0 && 
                userRecommendation.map((url, index) => {
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
            
            <div className="space-y-4">
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

          {/* Recommended Chat Sessions */}
          <div>
            <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              Recent Chat Sessions
            </h2>
            {recommendedChats.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
                {recommendedChats.map((chat) => (
                  <Card key={chat.id} className="group hover:shadow-lg transition-all duration-200 border-border/50 hover:border-border hover:scale-[1.02]">
                    <CardHeader className="pb-4 space-y-3">
                      <div className="flex flex-col items-center text-center space-y-3">
                        {/* Chat Icon */}
                        <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                          <MessageCircle className="h-6 w-6 text-primary" />
                        </div>
                        
                        {/* Session Name */}
                        <CardTitle className="text-lg font-semibold leading-tight w-full" title={chat.session_name}>
                          {chat.session_name}
                        </CardTitle>
                        
                        {/* Status Badge */}
                        <Badge variant="secondary" className="text-xs px-3 py-1 bg-green-50 text-green-700 border-green-200">
                          <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                          Active Session
                        </Badge>
                      </div>
                    </CardHeader>

                    <CardContent className="pt-0 pb-6">
                      <div className="space-y-4">
                        {/* Session Details */}
                        <div className="bg-muted/30 rounded-lg p-3 space-y-2">
                          <div className="flex items-center justify-evenly text-sm">
                            <span className="text-muted-foreground flex items-center gap-2">
                              <Clock className="h-4 w-4" />
                              Last active
                            </span>
                            <span className="font-medium text-foreground">{formatDate(chat.updated_at)}</span>
                          </div>
                          <div className="flex items-center justify-evenly text-sm">
                            <span className="text-muted-foreground flex items-center gap-2">
                              <Calendar className="h-4 w-4" />
                              Created
                            </span>
                            <span className="font-medium text-foreground">{formatDate(chat.created_at)}</span>
                          </div>
                          <div className="flex items-center justify-evenly text-sm">
                            <span className="text-muted-foreground flex items-center gap-2">
                              <FileText className="h-4 w-4" />
                              Session ID
                            </span>
                            <span className="font-medium text-foreground">#{chat.id}</span>
                          </div>
                        </div>

                        {/* Description */}
                        <p className="text-sm text-muted-foreground text-center leading-relaxed">
                          Continue your legal conversation and get personalized insights based on your previous interactions.
                        </p>

                        {/* Action Buttons */}
                        <div className="grid grid-cols-2 gap-3 pt-2">
                          <Link href={`/chat/${chat.id}`} className="block">
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="w-full h-9 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-all"
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              Preview
                            </Button>
                          </Link>
                          <Link href={`/chat/${chat.id}`} className="block">
                            <Button 
                              size="sm" 
                              className="w-full h-9 text-sm font-medium bg-primary hover:bg-primary/90 transition-all"
                            >
                              <MessageCircle className="h-4 w-4 mr-2" />
                              Continue
                            </Button>
                          </Link>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="p-6 text-center">
                <MessageCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-semibold mb-2">No Chat Sessions Yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start your first conversation to see recommendations here.
                </p>
                <Link href="/?reset=true">
                  <Button className="gap-2">
                    <MessageCircle className="h-4 w-4" />
                    Start New Chat
                  </Button>
                </Link>
              </Card>
            )}
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
