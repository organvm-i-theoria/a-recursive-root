'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface DebateSession {
  session_id: string
  council_id: string
  topic: any
  status: string
  created_at: string
}

export default function Home() {
  const [debates, setDebates] = useState<DebateSession[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDebates()
  }, [])

  const fetchDebates = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_URL}/api/v1/debates`)
      setDebates(response.data.debates || [])
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch debates')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <header className="mb-12 text-center">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          AI Council System
        </h1>
        <p className="text-xl text-gray-300">
          Live AI Debate Streaming Platform
        </p>
      </header>

      {/* Navigation */}
      <nav className="mb-8 flex justify-center gap-4">
        <Link
          href="/debate/new"
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
        >
          Start New Debate
        </Link>
        <Link
          href="/agents"
          className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg font-semibold transition-colors"
        >
          View Agents
        </Link>
        <Link
          href="/topics"
          className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg font-semibold transition-colors"
        >
          Browse Topics
        </Link>
      </nav>

      {/* Active Debates */}
      <section className="mb-12">
        <h2 className="text-3xl font-bold mb-6">Active Debates</h2>

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-gray-400">Loading debates...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
            <p className="text-red-200">Error: {error}</p>
            <button
              onClick={fetchDebates}
              className="mt-2 text-sm text-red-300 hover:text-red-100 underline"
            >
              Try again
            </button>
          </div>
        )}

        {!loading && !error && debates.length === 0 && (
          <div className="bg-gray-800 rounded-lg p-8 text-center">
            <p className="text-gray-400 mb-4">No active debates</p>
            <Link
              href="/debate/new"
              className="inline-block px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            >
              Start Your First Debate
            </Link>
          </div>
        )}

        {!loading && !error && debates.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {debates.map((debate) => (
              <Link
                key={debate.session_id}
                href={`/debate/${debate.session_id}`}
                className="block bg-gray-800 hover:bg-gray-750 rounded-lg p-6 transition-colors border border-gray-700 hover:border-blue-500"
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-xl font-semibold text-blue-400">
                    {debate.topic?.title || 'Untitled Debate'}
                  </h3>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    debate.status === 'active'
                      ? 'bg-green-900 text-green-200'
                      : 'bg-gray-700 text-gray-300'
                  }`}>
                    {debate.status}
                  </span>
                </div>
                <p className="text-gray-400 text-sm mb-4">
                  {debate.topic?.description || 'No description'}
                </p>
                <div className="text-xs text-gray-500">
                  Council: {debate.council_id}
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* System Status */}
      <section className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">System Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-700 rounded p-4">
            <div className="text-3xl font-bold text-blue-400 mb-2">
              {debates.length}
            </div>
            <div className="text-sm text-gray-400">Active Debates</div>
          </div>
          <div className="bg-gray-700 rounded p-4">
            <div className="text-3xl font-bold text-green-400 mb-2">
              Online
            </div>
            <div className="text-sm text-gray-400">System Status</div>
          </div>
          <div className="bg-gray-700 rounded p-4">
            <div className="text-3xl font-bold text-purple-400 mb-2">
              v0.2.0
            </div>
            <div className="text-sm text-gray-400">Version</div>
          </div>
        </div>
      </section>
    </div>
  )
}
