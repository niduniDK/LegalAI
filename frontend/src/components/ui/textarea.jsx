import * as React from "react"
import { cn } from "@/lib/utils"

const AutoResizeTextarea = React.forwardRef(({ className, ...props }, ref) => {
  const textareaRef = React.useRef(null)
  
  const adjustHeight = React.useCallback(() => {
    const textarea = textareaRef.current
    if (textarea) {
      // Reset height to auto to get the correct scrollHeight
      textarea.style.height = 'auto'
      // Set the height to the scrollHeight, but with min and max limits
      const scrollHeight = textarea.scrollHeight
      const minHeight = 40 // Minimum height (roughly equivalent to input field)
      const maxHeight = 200 // Maximum height before scrolling
      
      textarea.style.height = Math.min(Math.max(scrollHeight, minHeight), maxHeight) + 'px'
    }
  }, [])

  React.useEffect(() => {
    adjustHeight()
  }, [props.value, adjustHeight])

  React.useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.addEventListener('input', adjustHeight)
      return () => textarea.removeEventListener('input', adjustHeight)
    }
  }, [adjustHeight])

  const combinedRef = React.useCallback((node) => {
    textareaRef.current = node
    if (typeof ref === 'function') {
      ref(node)
    } else if (ref) {
      ref.current = node
    }
  }, [ref])

  return (
    <textarea
      ref={combinedRef}
      className={cn(
        "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input flex min-h-[40px] w-full min-w-0 rounded-md border bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none resize-none overflow-y-auto file:inline-flex file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
        "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
        className
      )}
      rows={1}
      {...props}
    />
  )
})

AutoResizeTextarea.displayName = "AutoResizeTextarea"

const Textarea = React.forwardRef(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input flex min-h-[60px] w-full min-w-0 rounded-md border bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm",
        "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]",
        "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
        className
      )}
      ref={ref}
      {...props}
    />
  )
})

Textarea.displayName = "Textarea"

export { Textarea, AutoResizeTextarea }