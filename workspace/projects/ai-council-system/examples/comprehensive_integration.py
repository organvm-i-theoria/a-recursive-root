"""
Comprehensive Integration Example - AI Council System

This example demonstrates how all components work together:
1. Event Ingestion
2. Topic Extraction
3. Agent Creation
4. Council Formation (placeholder)
5. Debate Execution (placeholder)

Run this to see the full pipeline in action.
"""

import asyncio
from datetime import datetime

# Import all core modules
from core.agents import (
    Agent,
    get_personality,
    LLMProviderFactory,
    MemoryManager,
    DebateContext,
)

from core.events import (
    IngestorFactory,
    EventProcessor,
    TopicExtractor,
    EventQueue,
    TopicQueue,
    EventSource,
)


async def main():
    print("=" * 70)
    print("AI Council System - Comprehensive Integration Example")
    print("=" * 70)
    print()

    # ============================================================
    # STEP 1: Event Ingestion
    # ============================================================
    print("STEP 1: Event Ingestion")
    print("-" * 70)

    # Create ingestors (using mock data for now)
    twitter = IngestorFactory.create_twitter(
        api_key="mock-key",
        keywords=["AI", "regulation", "cryptocurrency"]
    )

    news = IngestorFactory.create_news_api(
        api_key="mock-key",
        sources=["techcrunch", "bbc-news"]
    )

    # Fetch events
    print("📡 Fetching events from sources...")
    twitter_events = await twitter.fetch_events(limit=5)
    news_events = await news.fetch_events(limit=5)

    all_raw_events = twitter_events + news_events
    print(f"✅ Fetched {len(all_raw_events)} raw events")
    print(f"   - Twitter: {len(twitter_events)}")
    print(f"   - News API: {len(news_events)}")
    print()

    # ============================================================
    # STEP 2: Event Processing
    # ============================================================
    print("STEP 2: Event Processing")
    print("-" * 70)

    processor = EventProcessor()

    print("⚙️  Processing events...")
    processed_events = await processor.process_batch(all_raw_events)

    print(f"✅ Processed {len(processed_events)} events")
    print()
    print("📊 Sample Processed Event:")
    if processed_events:
        sample = processed_events[0]
        print(f"   Title: {sample.title}")
        print(f"   Category: {sample.category.value}")
        print(f"   Priority: {sample.priority.value}")
        print(f"   Importance: {sample.importance_score:.2f}")
        print(f"   Sentiment: {sample.sentiment:+.2f}")
        print(f"   Keywords: {', '.join(sample.keywords[:5])}")
        print(f"   Entities: {len(sample.entities)} extracted")
    print()

    # ============================================================
    # STEP 3: Topic Extraction
    # ============================================================
    print("STEP 3: Topic Extraction")
    print("-" * 70)

    extractor = TopicExtractor()

    print("🎯 Extracting debate topics...")
    topics = await extractor.extract_topics(
        processed_events,
        limit=3,
        min_controversy=0.3  # Lower for demo
    )

    print(f"✅ Extracted {len(topics)} debate topics")
    print()

    for i, topic in enumerate(topics, 1):
        print(f"📌 Topic {i}:")
        print(f"   Title: {topic.title}")
        print(f"   Category: {topic.category.value}")
        print(f"   Importance: {topic.importance_score:.2f}")
        print(f"   Controversy: {topic.controversy_score:.2f}")
        print(f"   Perspectives: {', '.join(topic.perspectives[:3])}")
        print(f"   Source Events: {len(topic.source_events)}")
        print()

    # ============================================================
    # STEP 4: Queue Management
    # ============================================================
    print("STEP 4: Queue Management")
    print("-" * 70)

    event_queue = EventQueue(max_size=100)
    topic_queue = TopicQueue(max_size=50)

    print("📥 Adding events and topics to queues...")
    event_queue.add_batch(processed_events)
    topic_queue.add_batch(topics)

    print(f"✅ Event Queue: {event_queue.size()} events")
    print(f"✅ Topic Queue: {topic_queue.available_count()} available topics")
    print()

    # Get next topic for debate
    next_topic = topic_queue.peek(1)[0] if topics else None

    if next_topic:
        print(f"🔥 Next Debate Topic:")
        print(f"   {next_topic.title}")
        print()

    # ============================================================
    # STEP 5: Agent Creation
    # ============================================================
    print("STEP 5: Agent Creation")
    print("-" * 70)

    # Create mock LLM provider for demo
    mock_llm = LLMProviderFactory.create_mock(responses=[
        "I believe this requires careful consideration of both benefits and risks.",
        "The evidence strongly suggests we should proceed with caution.",
        "This is a critical issue that demands immediate attention.",
        "We need a balanced approach that considers all stakeholders.",
        "The data is clear - we must act decisively.",
    ])

    # Create 5 agents with different personalities
    print("🤖 Creating AI agents with diverse personalities...")

    agent_configs = [
        ("agent_001", "pragmatist"),
        ("agent_002", "idealist"),
        ("agent_003", "skeptic"),
        ("agent_004", "economist"),
        ("agent_005", "ethicist"),
    ]

    agents = []
    for agent_id, personality_name in agent_configs:
        personality = get_personality(personality_name)
        memory = MemoryManager(agent_id)
        await memory.initialize()

        agent = Agent(
            agent_id=agent_id,
            personality=personality,
            llm_provider=mock_llm,
            memory_manager=memory
        )
        await agent.initialize()
        agents.append(agent)

        print(f"   ✅ {personality.name} ({personality.archetype})")

    print()

    # ============================================================
    # STEP 6: Debate Context Setup
    # ============================================================
    print("STEP 6: Debate Context Setup")
    print("-" * 70)

    if next_topic:
        # Create debate context
        context = DebateContext(
            topic=next_topic.title,
            description=next_topic.description,
            perspectives=next_topic.perspectives,
            background_info=next_topic.background_info,
            participants=[a.agent_id for a in agents],
            rules={
                "max_rounds": 3,
                "response_time_limit": 30,
                "voting_required": True,
            }
        )

        print(f"📋 Debate Context Created:")
        print(f"   Topic: {context.topic}")
        print(f"   Participants: {len(context.participants)} agents")
        print(f"   Perspectives: {len(context.perspectives)}")
        print()

        # Set context for all agents
        for agent in agents:
            await agent.set_context(context)

        print("✅ All agents briefed on debate topic")
        print()

        # ============================================================
        # STEP 7: Sample Debate Round
        # ============================================================
        print("STEP 7: Sample Debate Round (Mock)")
        print("-" * 70)
        print()

        print("🎤 Opening Statements:")
        print()

        responses = []
        for agent in agents:
            response = await agent.respond(
                f"What is your position on: {context.topic}?",
                context=context
            )
            responses.append(response)

            print(f"💬 {agent.personality.name}:")
            print(f"   {response.content}")
            print(f"   (Confidence: {response.confidence:.2f})")
            print()

        # ============================================================
        # STEP 8: Voting
        # ============================================================
        print("STEP 8: Voting")
        print("-" * 70)
        print()

        # Create voting options from perspectives
        voting_options = next_topic.perspectives[:3] if len(next_topic.perspectives) >= 3 else [
            "Strongly Support",
            "Neutral/Cautious",
            "Strongly Oppose"
        ]

        print(f"🗳️  Voting Options:")
        for i, option in enumerate(voting_options, 1):
            print(f"   {i}. {option}")
        print()

        votes = []
        vote_tally = {option: 0 for option in voting_options}

        for agent in agents:
            vote = await agent.vote(voting_options, context=context)
            votes.append(vote)
            vote_tally[vote.option] += vote.weight

            print(f"🗳️  {agent.personality.name} votes: {vote.option}")
            print(f"   Reasoning: {vote.reasoning[:100]}...")
            print(f"   Weight: {vote.weight:.2f}")
            print()

        # ============================================================
        # STEP 9: Results
        # ============================================================
        print("STEP 9: Debate Results")
        print("-" * 70)
        print()

        print("📊 Vote Tally:")
        for option, weight in sorted(vote_tally.items(), key=lambda x: x[1], reverse=True):
            print(f"   {option}: {weight:.2f}")

        winner = max(vote_tally.items(), key=lambda x: x[1])[0]
        print()
        print(f"🏆 Outcome: {winner}")
        print()

    else:
        print("⚠️  No topics available for debate")
        print()

    # ============================================================
    # STEP 10: Statistics
    # ============================================================
    print("STEP 10: System Statistics")
    print("-" * 70)
    print()

    print("📈 Ingestion Stats:")
    print(f"   Twitter: {twitter.get_stats()}")
    print(f"   News API: {news.get_stats()}")
    print()

    print("📈 Processing Stats:")
    print(f"   Processor: {processor.get_stats()}")
    print(f"   Extractor: {extractor.get_stats()}")
    print()

    print("📈 Queue Stats:")
    print(f"   Event Queue: {event_queue.get_stats()}")
    print(f"   Topic Queue: {topic_queue.get_stats()}")
    print()

    print("📈 Agent Stats:")
    for agent in agents:
        history = await agent.get_response_history()
        votes_history = await agent.get_vote_history()
        memory_stats = agent.memory_manager.get_stats()

        print(f"   {agent.personality.name}:")
        print(f"      Responses: {len(history)}")
        print(f"      Votes: {len(votes_history)}")
        print(f"      Memory: {memory_stats['total_stored']} stored")
    print()

    # ============================================================
    # Summary
    # ============================================================
    print("=" * 70)
    print("✅ Integration Example Complete!")
    print("=" * 70)
    print()
    print("This example demonstrated:")
    print("  1. ✅ Event ingestion from multiple sources")
    print("  2. ✅ Event processing and enrichment")
    print("  3. ✅ Debate topic extraction")
    print("  4. ✅ Priority queue management")
    print("  5. ✅ AI agent creation with personalities")
    print("  6. ✅ Debate context setup")
    print("  7. ✅ Agent responses and discussion")
    print("  8. ✅ Voting with reasoning")
    print("  9. ✅ Results tabulation")
    print("  10. ✅ System statistics tracking")
    print()
    print("🚀 All core components are functional and integrated!")
    print()


if __name__ == "__main__":
    # Run the comprehensive example
    asyncio.run(main())
