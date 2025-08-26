"use client"

import * as React from "react"
import { MessageCircle, Compass, Star, History, Scale, Plus, Search } from 'lucide-react'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { usePathname } from "next/navigation"

const navigationItems = [
  {
    title: "Chat",
    url: "/",
    icon: MessageCircle,
    description: "Start a new legal conversation"
  },
  {
    title: "Discover",
    url: "/discover",
    icon: Compass,
    description: "Explore legal documents and insights"
  },
  {
    title: "Recommendations",
    url: "/recommendations",
    icon: Star,
    description: "Personalized legal suggestions"
  },
  {
    title: "History",
    url: "/history",
    icon: History,
    description: "View past conversations and queries"
  },
]

export function AppSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar variant="inset" className="border-r border-border/40">
      <SidebarHeader className="border-b border-border/40 p-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Scale className="h-4 w-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold">LegalAI</span>
            <span className="text-xs text-muted-foreground">Sri Lanka</span>
          </div>
        </div>
      </SidebarHeader>
      
      <SidebarContent className="p-2">
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <Button 
                  className="w-full justify-start gap-2 h-9 mb-2" 
                  size="sm"
                  asChild
                >
                  <Link href="/">
                    <Plus className="h-4 w-4" />
                    New Chat
                  </Link>
                </Button>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-xs font-medium text-muted-foreground px-2 mb-2">
            Navigation
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton 
                    asChild 
                    isActive={pathname === item.url}
                    tooltip={item.description}
                  >
                    <Link href={item.url} className="flex items-center gap-3 px-2 py-2">
                      <item.icon className="h-4 w-4" />
                      <span className="text-sm">{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-border/40 p-4">
        <div className="text-xs text-muted-foreground">
          <p>Legal information for Sri Lanka</p>
        </div>
      </SidebarFooter>
      
      <SidebarRail />
    </Sidebar>
  )
}
