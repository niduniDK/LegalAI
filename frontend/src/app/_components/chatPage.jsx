"use client"

import React, { useEffect, useState, useRef } from 'react';
import { FileText, Send, Scale } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import ReactMarkdown from 'react-markdown'
import { useAuth } from '@/contexts/AuthContext';

const ChatPage = ({ sessionId }) => {
    const { token, logout } = useAuth();
    const [messages, setMessages] = useState([]);
    const [resources, setResources] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [language, setLanguage] = useState("en");
    const scrollAreaRef = useRef(null);

    // Fetch chat history on mount or sessionId change
    useEffect(() => {
        const fetchChatHistory = async () => {
            if (!token) {
                console.warn("No authentication token available");
                return;
            }
            
            setIsLoading(true);
            try {
                const response = await fetch(`http://localhost:8000/chat-history/sessions/${sessionId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                });
                
                if (response.status === 401) {
                    console.error("Token expired or invalid. Please log in again.");
                    logout();
                    return;
                }
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                // Transform the messages to match the ChatInterface format
                const transformedMessages = (data.messages || []).map((msg, index) => ({
                    id: msg.id || index.toString(),
                    content: msg.message_content || msg.content || msg.text,
                    role: msg.message_role || (msg.role === 'ai' ? 'assistant' : msg.role),
                    timestamp: msg.created_at ? new Date(msg.created_at) : new Date(),
                }));
                
                setMessages(transformedMessages);
            } catch (error) {
                console.error('Failed to load chat history:', error);
            }
            setIsLoading(false);
        };
        if (sessionId) fetchChatHistory();
    }, [sessionId, token, logout]);

    // Send message handler
    const handleSend = async () => {
        if (!input.trim() || !token) return;
        
        const userMessage = {
            id: Date.now().toString(),
            content: input,
            role: "user",
            timestamp: new Date(),
        };
        
        setMessages((prev) => [...prev, userMessage]);
        const currentInput = input;
        setInput('');
        setIsLoading(true);
        
        try {
            // First add the message to the session
            const addMessageResponse = await fetch(`http://localhost:8000/chat-history/sessions/${sessionId}/messages`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ 
                    role: 'user',
                    content: currentInput 
                }),
            });
            
            if (addMessageResponse.status === 401) {
                console.error("Token expired or invalid. Please log in again.");
                logout();
                return;
            }
            
            // Get AI response
            const aiResponse = await fetch('http://localhost:8000/chat/get_ai_response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ query: currentInput, history: messages}),
            });
            
            if (!aiResponse.ok) {
                throw new Error(`HTTP error! status: ${aiResponse.status}`);
            }
            
            const aiData = await aiResponse.json();
            
            const assistantMessage = {
                id: (Date.now() + 1).toString(),
                content: aiData.response,
                role: "assistant",
                timestamp: new Date(),
            };
            
            setMessages((prev) => [...prev, assistantMessage]);
            setResources(aiData.files || []);
            
            // Add AI response to session
            await fetch(`http://localhost:8000/chat-history/sessions/${sessionId}/messages`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ 
                    role: 'assistant',
                    content: aiData.response 
                }),
            });
            
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                id: (Date.now() + 1).toString(),
                content: "Sorry, I encountered an error. Please try again.",
                role: "assistant",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        }
        setIsLoading(false);
    };

    const handleKeyPress = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div className="flex flex-col h-screen border rounded-xl p-4">
            {/* Chat Messages */}
            <ScrollArea className="flex-1 overflow-y-auto scrollbar-hide" ref={scrollAreaRef}>
                {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
                        <Scale className="h-10 w-10 mb-2" />
                        <h2 className="text-xl font-semibold">Chat Session</h2>
                        <p>Continue your conversation or ask a new question.</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {messages.map(msg => (
                            <div key={msg.id}>
                                <div className={`flex ${msg.role === "user" ? "justify-end mr-10" : "justify-start ml-10"}`}>
                                    <div className={`max-w-[70%] px-4 py-2 rounded-2xl ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                                        <div className="whitespace-pre-wrap text-sm">
                                            <ReactMarkdown
                                                components={{
                                                    p: ({children}) => <p className="mb-2 last:mb-0">{children}</p>,
                                                    ul: ({children}) => <ul className="list-disc ml-4 mb-2">{children}</ul>,
                                                    ol: ({children}) => <ol className="list-decimal ml-4 mb-2">{children}</ol>,
                                                    li: ({children}) => <li className="mb-1">{children}</li>,
                                                    strong: ({children}) => <strong className="font-semibold">{children}</strong>,
                                                    em: ({children}) => <em className="italic">{children}</em>,
                                                    code: ({children}) => <code className="bg-gray-200 px-1 rounded text-xs">{children}</code>,
                                                    pre: ({children}) => <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">{children}</pre>,
                                                    h1: ({children}) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
                                                    h2: ({children}) => <h2 className="text-md font-semibold mb-2">{children}</h2>,
                                                    h3: ({children}) => <h3 className="text-sm font-medium mb-1">{children}</h3>,
                                                }}
                                            >
                                                {msg.content}
                                            </ReactMarkdown>
                                        </div>
                                    </div>
                                </div>
                                {msg.role !== "user" && Array.isArray(resources) && resources.length > 0 && (
                                    <div className="mt-2 min-w-full px-2">
                                        <div className="border-t pt-4">
                                            <h3 className="text-lg font-semibold mb-3 text-foreground flex items-center">
                                                <FileText className="h-5 w-5 mr-2" />
                                                Related Documents ({resources.length})
                                            </h3>
                                            <div className="min-w-full grid gap-2 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
                                                {resources.map((url, index) => {
                                                    // Extract document type and filename
                                                    let docType = "Document"
                                                    let filename = ""
                                                    const basePath = "https://documents.gov.lk/view/"
                                                    if (url.startsWith(basePath)) {
                                                        const afterBase = url.slice(basePath.length)
                                                        const parts = afterBase.split("/")
                                                        if (parts.length > 1) {
                                                            docType = parts[0]
                                                            filename = parts.slice(1).join("/")
                                                        }
                                                    }
                                                    // Capitalize docType and handle known types
                                                    let badgeText = docType
                                                    if (["bills", "acts", "gazettes", "constitution"].includes(docType.toLowerCase())) {
                                                        badgeText = docType.charAt(0).toUpperCase() + docType.slice(1)
                                                    } else {
                                                        badgeText = "PDF"
                                                    }
                                                    return (
                                                        <Card key={index} className="overflow-hidden hover:shadow-lg transition-all duration-200 border-border/50 hover:border-border w-full">
                                                            <CardContent className="p-1">
                                                                <div className="flex flex-col gap-2 p-2 bg-muted/20 rounded-lg border cursor-pointer hover:bg-muted/40 transition-colors" onClick={() => window.open(url, '_blank')}>
                                                                    <div className="flex items-center justify-between">
                                                                        <div className="flex items-center gap-1 min-w-0 flex-1">
                                                                            <FileText className="h-3 w-3 text-primary shrink-0" />
                                                                            <span className="text-xs font-medium truncate">
                                                                                {filename || `Document ${index + 1}`}
                                                                            </span>
                                                                        </div>
                                                                        <Badge variant="secondary" className="text-xs ml-1 shrink-0">
                                                                            {badgeText}
                                                                        </Badge>
                                                                    </div>
                                                                </div>
                                                            </CardContent>
                                                        </Card>
                                                    )
                                                })}
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="max-w-[70%] rounded-2xl bg-muted px-4 py-3 animate-pulse">
                                    <div className="flex space-x-1">
                                        <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce"></div>
                                        <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{animationDelay: '0.1s'}}></div>
                                        <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{animationDelay: '0.2s'}}></div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </ScrollArea>

            {/* Input Area */}
            <div className="mt-4 flex items-center space-x-2">
                <Input
                    placeholder="Ask a question..."
                    className="flex-1"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={isLoading}
                />
                <Button onClick={handleSend} disabled={!input.trim() || isLoading}>
                    <Send className="h-4 w-4" />
                </Button>
            </div>
        </div>
    );
};

export default ChatPage;