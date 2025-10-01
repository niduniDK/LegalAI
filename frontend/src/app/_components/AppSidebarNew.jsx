"use client"

import * as React from "react"
import { MessageCircle, Compass, Star, History, Scale, Plus, LogOut, User } from 'lucide-react'
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
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { useAuth } from "@/contexts/AuthContext"

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
  }
]

export function AppSidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout, isAuthenticated, token } = useAuth()

  const [chats, setChats] = React.useState([])
  const [isLoadingChats, setIsLoadingChats] = React.useState(false)

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  React.useEffect(() => {
    const fetchChatSessions = async () => {
      if (!token) {
        return
      }

      setIsLoadingChats(true)
      try{
        const response = await fetch("http://localhost:8000/chat-history/user_sessions", {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            ...(token && { "Authorization": `Bearer ${token}` })
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
        // Only show the 5 most recent chats to avoid clutter
        setChats((data || []).slice(0, 5))
      } catch (error) {
        console.error('Error fetching chat history:', error)
        setChats([])
      } finally {
        setIsLoadingChats(false)
      }
    }
    
    fetchChatSessions()
  }, [token, logout])

  // Don't show sidebar on auth pages
  if (pathname === '/login' || pathname === '/register' || pathname === '/reset-password') {
    return null
  }

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
        {isAuthenticated ? (
          <>
            {/* New Chat Section */}
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <Button 
                      className="w-full justify-start gap-2 h-10 mb-3 bg-primary hover:bg-primary/90" 
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

            {/* Navigation Section */}
            <SidebarGroup>
              <SidebarGroupLabel className="text-xs font-medium text-muted-foreground px-2 mb-2">
                Features
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
                        <Link href={item.url} className="flex items-center gap-3 px-2 py-2 rounded-md hover:bg-accent">
                          <item.icon className="h-4 w-4" />
                          <span className="text-sm">{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>

            {/* Recent Chats Section */}
            <SidebarGroup>
              <div className="flex items-center justify-between px-2 mb-2">
                <SidebarGroupLabel className="text-xs font-medium text-muted-foreground">
                  Recent Chats
                </SidebarGroupLabel>
                {chats.length > 0 && (
                  <Link href="/history" className="text-xs text-primary hover:underline">
                    View All
                  </Link>
                )}
              </div>
              <SidebarGroupContent>
                <SidebarMenu>
                  {isLoadingChats ? (
                    <SidebarMenuItem>
                      <div className="flex items-center gap-2 px-2 py-2 text-xs text-muted-foreground">
                        <MessageCircle className="h-4 w-4 animate-pulse" />
                        <span>Loading chats...</span>
                      </div>
                    </SidebarMenuItem>
                  ) : chats.length > 0 ? (
                    chats.map((chat) => (
                      <SidebarMenuItem key={chat.id}>
                        <SidebarMenuButton 
                          asChild 
                          isActive={pathname === `/chat/${chat.id}`}
                          tooltip={chat.session_name}
                        >
                          <Link href={`/chat/${chat.id}`} className="flex items-center gap-3 px-2 py-2 rounded-md hover:bg-accent">
                            <MessageCircle className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm truncate">{chat.session_name}</span>
                          </Link>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    ))
                  ) : (
                    <SidebarMenuItem>
                      <div className="px-2 py-2">
                        <p className="text-xs text-muted-foreground text-center">
                          No recent chats
                        </p>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="w-full mt-2 h-8 text-xs"
                          asChild
                        >
                          <Link href="/">
                            Start chatting
                          </Link>
                        </Button>
                      </div>
                    </SidebarMenuItem>
                  )}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </>
        ) : (
          /* Guest User Section */
          <SidebarGroup>
            <SidebarGroupLabel className="text-xs font-medium text-muted-foreground px-2 mb-2">
              Get Started
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <Button 
                    className="w-full justify-start gap-2 h-10 mb-2" 
                    size="sm"
                    asChild
                  >
                    <Link href="/login">
                      <User className="h-4 w-4" />
                      Sign In
                    </Link>
                  </Button>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <Button 
                    className="w-full justify-start gap-2 h-10" 
                    size="sm"
                    variant="outline"
                    asChild
                  >
                    <Link href="/register">
                      <Plus className="h-4 w-4" />
                      Sign Up
                    </Link>
                  </Button>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}
      </SidebarContent>

      <SidebarFooter className="border-t border-border/40 p-4">
        {isAuthenticated && user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="w-full justify-start h-auto p-2">
                <div className="flex items-center gap-2 text-left">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground text-sm">
                    {user.first_name ? user.first_name[0].toUpperCase() : user.email[0].toUpperCase()}
                  </div>
                  <div className="flex flex-col flex-1 min-w-0">
                    <span className="text-sm font-medium truncate">
                      {user.first_name && user.last_name 
                        ? `${user.first_name} ${user.last_name}` 
                        : user.email}
                    </span>
                    <span className="text-xs text-muted-foreground truncate">
                      {user.email}
                    </span>
                  </div>
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-56">
              <DropdownMenuItem asChild>
                <Link href="/profile" className="cursor-pointer">
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
                <LogOut className="mr-2 h-4 w-4" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <div className="text-xs text-muted-foreground">
            <p>Legal information for Sri Lanka</p>
          </div>
        )}
      </SidebarFooter>
      
      <SidebarRail />
    </Sidebar>
  )
}
