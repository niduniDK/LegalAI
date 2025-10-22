'use client';

import { useState } from 'react';
import { ChatBox } from './_components/ChatBox';
import { ChatInterface } from './_components/ChatInterface';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';

export default function HomePage() {
  const { token, logout } = useAuth();
  const [chatStarted, setChatStarted] = useState(false);
  const [initialQuery, setInitialQuery] = useState('');
  const [sessionName, setSessionName] = useState('');
  const [chat_id, setChatId] = useState(null);

  const handleNewChat = useCallback(() => {
    setChatStarted(false)
    setInitialQuery("")
    setSessionName("")
    setChatId(null)
  }, [])

  // Reset chat when navigating with reset parameter
  useEffect(() => {
    if (searchParams.get('reset') === 'true') {
      handleNewChat()
    }
  }, [searchParams, handleNewChat])

  const handleStartChat = (query) => {
    setInitialQuery(query);
    setChatStarted(true);
    createChatSession(query);
  };

  const createChatSession = async (query) => {
    if (!token) {
      console.warn('No authentication token available');
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/chat-history/sessions`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
          },
          body: JSON.stringify({ session_name: query }),
        }
      );

      if (response.status === 401) {
        console.error('Token expired or invalid. Please log in again.');
        logout();
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSessionName(data.session_name);
      setChatId(data.id);
      console.log('Created chat session:', data);
    } catch (error) {
      console.error('Error creating chat session:', error);
    }
  };

  return (
    <ProtectedRoute>
      <div className='flex h-screen'>
        <main className='flex-1 flex flex-col items-center justify-center p-8'>
          <div className='w-full max-w-2xl space-y-8'>
            <div className='text-center'>
              <h1 className='text-4xl font-medium text-foreground mb-8'>
                Break Legal jargon here.
              </h1>
            </div>

            {chatStarted ? (
              <ChatInterface
                initialQuery={initialQuery}
                chat_id={chat_id}
                session_name={sessionName}
              />
            ) : (
              <ChatBox onStartChat={handleStartChat} />
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
