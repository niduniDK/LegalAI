import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Focus, Paperclip, Zap, ChevronDown, ArrowRight } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useState } from "react"

export function ChatBox({ onStartChat }) {
  const [query, setQuery] = useState("")

  const handleSendMessage = () => {
    if (query.trim()) {
      onStartChat(query)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="w-full space-y-4">
      <div className="relative">
        <Input
          placeholder="Ask anything..."
          className="w-full h-14 px-4 text-lg bg-card border-border rounded-xl pr-12"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <Button
          size="icon"
          className="absolute right-2 top-2 h-10 w-10 rounded-lg"
          onClick={handleSendMessage}
        >
          <ArrowRight className="h-4 w-4" />
        </Button>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center space-x-3">
        <Button variant="outline" size="sm" className="flex items-center space-x-2 rounded-lg bg-transparent">
          <Focus className="h-4 w-4" />
          <span>Focus</span>
        </Button>

        <Button variant="outline" size="sm" className="flex items-center space-x-2 rounded-lg bg-transparent">
          <Paperclip className="h-4 w-4" />
          <span>Attach</span>
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="flex items-center space-x-2 rounded-lg bg-transparent">
              <Zap className="h-4 w-4 text-yellow-500" />
              <span>Speed</span>
              <ChevronDown className="h-3 w-3" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem>Fast</DropdownMenuItem>
            <DropdownMenuItem>Balanced</DropdownMenuItem>
            <DropdownMenuItem>Quality</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
