'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams } from 'next/navigation'
import axios from 'axios'
import { io, Socket } from 'socket.io-client'
import ReactMarkdown from 'react-markdown'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'

interface Agent {
  agent_id: string
  personality: string
  state: string
}

interface DebateMessage {
  agent_id: string
  content: string
  timestamp: string
  round: number
  type: 'opening' | 'discussion' | 'vote'
}

interface VoteResult {
  option: string
  votes: number
  reasoning: string[]
}

interface DebateSession {
  session_id: string
  council_id: string
  topic: any
  status: string
  messages: DebateMessage[]
  votes: VoteResult[]
}

export default function DebateViewer() {
  const params = useParams()
  const sessionId = params.id as string

  const [session, setSession] = useState<DebateSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [connected, setConnected] = useState(false)
  const [liveUpdates, setLiveUpdates] = useState<any[]>([])

  const socketRef = useRef<Socket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchSession()
    connectWebSocket()

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect()
      }
    }
  }, [sessionId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [session?.messages, liveUpdates])

  const fetchSession = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/api/v1/debates/${sessionId}`)
      setSession(response.data.session)
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch debate')
    } finally {
      setLoading(false)
    }
  }

  const connectWebSocket = () => {
    const socket = io(WS_URL)

    socket.on('connect', () => {
      console.log('WebSocket connected')
      setConnected(true)
      socket.emit('subscribe', { topics: [`debate:${sessionId}`] })
    })

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
      setConnected(false)
    })

    socket.on('debate_update', (data: any) => {
      console.log('Debate update:', data)
      setLiveUpdates(prev => [...prev, data])

      // Refresh session data
      if (data.session_id === sessionId) {
        fetchSession()
      }
    })

    socket.on('agent_response', (data: any) => {
      console.log('Agent response:', data)
      setLiveUpdates(prev => [...prev, { type: 'agent_response', ...data }])
    })

    socketRef.current = socket
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-400">Loading debate...</p>
        </div>
      </div>
    )
  }

  if (error || !session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-6 max-w-md">
          <h2 className="text-xl font-bold mb-2">Error</h2>
          <p className="text-red-200">{error || 'Debate not found'}</p>
          <button
            onClick={fetchSession}
            className="mt-4 px-4 py-2 bg-red-700 hover:bg-red-600 rounded transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            {session.topic?.title || 'Live Debate'}
          </h1>
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${
              connected ? 'bg-green-900' : 'bg-red-900'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'
              }`}></div>
              <span className="text-sm">{connected ? 'Live' : 'Offline'}</span>
            </div>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
              session.status === 'active'
                ? 'bg-blue-900 text-blue-200'
                : session.status === 'completed'
                ? 'bg-green-900 text-green-200'
                : 'bg-gray-700 text-gray-300'
            }`}>
              {session.status}
            </span>
          </div>
        </div>
        {session.topic?.description && (
          <p className="text-gray-400 text-lg">{session.topic.description}</p>
        )}
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main debate area */}
        <div className="lg:col-span-2">
          <div className="bg-gray-800 rounded-lg p-6 min-h-[600px] max-h-[800px] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4 sticky top-0 bg-gray-800 pb-2">
              Debate Transcript
            </h2>

            {session.messages && session.messages.length > 0 ? (
              <div className="space-y-6">
                {session.messages.map((message, idx) => (
                  <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-blue-400">
                        {message.agent_id}
                      </span>
                      <span className="text-xs text-gray-500">
                        Round {message.round} • {message.type}
                      </span>
                    </div>
                    <div className="markdown text-gray-300">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <p>No messages yet. Debate will start soon...</p>
              </div>
            )}

            {/* Live updates indicator */}
            {liveUpdates.length > 0 && session.status === 'active' && (
              <div className="mt-4 p-3 bg-blue-900/30 border border-blue-500 rounded animate-pulse-slow">
                <p className="text-sm text-blue-300">
                  Receiving live updates... ({liveUpdates.length} events)
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Council Members */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4">Council Members</h3>
            <div className="space-y-3">
              {session.topic?.perspectives?.map((perspective: string, idx: number) => (
                <div key={idx} className="bg-gray-700 rounded p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 rounded-full bg-green-400"></div>
                    <span className="font-semibold text-sm">Agent {idx + 1}</span>
                  </div>
                  <p className="text-xs text-gray-400">{perspective}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Voting Results */}
          {session.votes && session.votes.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">Voting Results</h3>
              <div className="space-y-4">
                {session.votes.map((result, idx) => (
                  <div key={idx}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold">{result.option}</span>
                      <span className="text-blue-400 font-bold">{result.votes}</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all"
                        style={{
                          width: `${(result.votes / session.votes.reduce((sum, v) => sum + v.votes, 0)) * 100}%`
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Session Info */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4">Session Info</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Session ID:</span>
                <span className="font-mono text-xs">{session.session_id.slice(0, 8)}...</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Council:</span>
                <span className="font-mono text-xs">{session.council_id.slice(0, 8)}...</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Status:</span>
                <span className="capitalize">{session.status}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
