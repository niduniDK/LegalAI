"use client"

import * as React from "react"
import { Star, MessageCircle, FileText, Clock } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"

const recommendations = [
  {
    id: "1",
    title: "Business Registration Requirements",
    category: "Corporate Law",
    relevanceScore: 95,
    reason: "Based on your recent queries about starting a business",
    summary: "Complete guide to registering a business in Sri Lanka, including required documents and procedures.",
    estimatedReadTime: "8 min",
    lastUpdated: "2024-01-15",
    tags: ["Business", "Registration", "Startup"],
    actionType: "document" 
  },
  {
    id: "2",
    title: "Employment Contract Templates",
    category: "Labor Law",
    relevanceScore: 88,
    reason: "Frequently accessed by users with similar interests",
    summary: "Standard employment contract templates compliant with Sri Lankan labor laws.",
    estimatedReadTime: "12 min",
    lastUpdated: "2024-02-01",
    tags: ["Employment", "Contracts", "HR"],
    actionType: "document" 
  }
]


export function RecommendationsInterface() {
  return (
    <div className="flex h-screen flex-col">
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
                          <Button size="sm" className="h-8 text-xs">
                            <MessageCircle className="h-3 w-3 mr-1" />
                            Start Chat
                          </Button>
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
              <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow">
                <div className="text-center">
                  <MessageCircle className="h-8 w-8 mx-auto mb-2 text-primary" />
                  <h3 className="font-medium text-sm mb-1">Ask Legal Question</h3>
                  <p className="text-xs text-muted-foreground">Get instant answers from our AI</p>
                </div>
              </Card>
              <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow">
                <div className="text-center">
                  <FileText className="h-8 w-8 mx-auto mb-2 text-primary" />
                  <h3 className="font-medium text-sm mb-1">Browse Documents</h3>
                  <p className="text-xs text-muted-foreground">Explore legal documents and acts</p>
                </div>
              </Card>
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
