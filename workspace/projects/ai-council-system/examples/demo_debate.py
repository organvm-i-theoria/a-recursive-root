#!/usr/bin/env python3
"""
AI Council System - Working Prototype Demo

This demo runs a complete end-to-end debate:
1. Ingest events from sources
2. Extract debate topic
3. Form AI council
4. Run structured debate
5. Collect votes
6. Display results

Usage:
    python demo_debate.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agents import (
    Agent,
    get_personality,
    get_all_personalities,
    LLMProviderFactory,
    MemoryManager,
    DebateContext,
)

from core.events import (
    IngestorFactory,
    EventProcessor,
    TopicExtractor,
    TopicQueue,
)

from core.council import (
    CouncilManager,
    DebateSessionManager,
)


def print_banner(text: str):
    """Print formatted banner"""
    print()
    print("=" * 70)
    print(f"  {text}")
    print("=" * 70)
    print()


def print_section(text: str):
    """Print section header"""
    print()
    print("-" * 70)
    print(f"  {text}")
    print("-" * 70)
    print()


async def main():
    """Run the AI Council debate demo"""

    print_banner("🏛️  AI COUNCIL SYSTEM - WORKING PROTOTYPE")

    print("This demo demonstrates a complete AI council debate:")
    print("  • Event ingestion from multiple sources")
    print("  • Automated topic extraction")
    print("  • Council formation with diverse personalities")
    print("  • Multi-round structured debate")
    print("  • Voting with reasoning")
    print("  • Results and transcript generation")
    print()
    input("Press ENTER to start the demo...")

    # ===================================================================
    # PHASE 1: Event Ingestion & Topic Selection
    # ===================================================================
    print_section("PHASE 1: Event Ingestion & Topic Selection")

    print("📡 Setting up event ingestors...")
    twitter = IngestorFactory.create_twitter(
        api_key="demo-key",
        keywords=["AI", "regulation", "ethics", "cryptocurrency"]
    )
    news = IngestorFactory.create_news_api(
        api_key="demo-key",
        sources=["techcrunch", "bbc-news", "reuters"]
    )
    print("✅ Ingestors configured")
    print()

    print("📥 Fetching events...")
    twitter_events = await twitter.fetch_events(limit=3)
    news_events = await news.fetch_events(limit=2)
    all_events = twitter_events + news_events
    print(f"✅ Fetched {len(all_events)} events")
    print()

    print("⚙️  Processing events...")
    processor = EventProcessor()
    processed = await processor.process_batch(all_events)
    print(f"✅ Processed {len(processed)} events")
    print()

    for i, event in enumerate(processed, 1):
        print(f"   {i}. {event.title}")
        print(f"      Category: {event.category.value} | "
              f"Importance: {event.importance_score:.2f} | "
              f"Sentiment: {event.sentiment:+.2f}")

    print()
    print("🎯 Extracting debate topics...")
    extractor = TopicExtractor()
    topics = await extractor.extract_topics(
        processed,
        limit=3,
        min_controversy=0.3
    )
    print(f"✅ Generated {len(topics)} potential topics")
    print()

    if not topics:
        print("❌ No topics generated. Please try again.")
        return

    # Display topics
    for i, topic in enumerate(topics, 1):
        print(f"   Topic {i}: {topic.title}")
        print(f"      Importance: {topic.importance_score:.2f} | "
              f"Controversy: {topic.controversy_score:.2f}")
        print(f"      Perspectives: {', '.join(topic.perspectives[:3])}")
        print()

    # Select first topic for debate
    selected_topic = topics[0]
    print(f"🔥 Selected for debate: {selected_topic.title}")
    print()

    input("Press ENTER to form the council...")

    # ===================================================================
    # PHASE 2: Council Formation
    # ===================================================================
    print_section("PHASE 2: Council Formation")

    print("🤖 Creating AI agent pool...")

    # Create mock LLM with varied responses
    mock_llm = LLMProviderFactory.create_mock(responses=[
        "I believe this issue requires careful analysis of all stakeholder perspectives. "
        "While there are valid concerns on both sides, the evidence suggests we need a "
        "balanced approach that maximizes benefit while minimizing harm.",

        "This is fundamentally about our values as a society. We must prioritize "
        "human dignity, fairness, and the greater good. The path forward should be "
        "guided by ethical principles, not just practical considerations.",

        "I remain skeptical of claims that aren't backed by rigorous evidence. "
        "Before we make any decisions, we need comprehensive data and peer-reviewed "
        "research. Anecdotes and speculation won't cut it.",

        "The economic implications cannot be ignored. We need to consider incentives, "
        "market dynamics, and long-term financial sustainability. What works in theory "
        "may fail in practice if the economics don't add up.",

        "Looking ahead, this represents a transformative opportunity. We shouldn't "
        "be constrained by current limitations. Bold vision and innovation can "
        "fundamentally change the landscape if we have the courage to pursue it.",
    ])

    # Create agents with different personalities
    agent_personalities = [
        "pragmatist",
        "idealist",
        "skeptic",
        "economist",
        "visionary",
    ]

    agents = []
    for personality_name in agent_personalities:
        agent_id = f"agent_{personality_name}"
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
    print(f"✅ Created pool of {len(agents)} agents")
    print()

    # Form council
    print("🏛️  Forming council...")
    council_manager = CouncilManager()
    council = await council_manager.form_council(
        topic_id=selected_topic.topic_id,
        available_agents=agents,
        council_size=5,
        method="diverse"
    )

    print(f"✅ Council formed: {council.council_id}")
    print(f"   Members: {', '.join(council.metadata['personalities'])}")
    print()

    input("Press ENTER to start the debate...")

    # ===================================================================
    # PHASE 3: Debate Execution
    # ===================================================================
    print_section("PHASE 3: Debate Execution")

    # Create debate context
    context = DebateContext(
        topic=selected_topic.title,
        description=selected_topic.description,
        perspectives=selected_topic.perspectives,
        background_info=selected_topic.background_info,
        participants=[a.agent_id for a in agents],
        rules={
            "max_rounds": 2,  # 2 discussion rounds + opening
            "response_time_limit": 30,
            "voting_required": True,
        }
    )

    # Set context for all agents
    for agent in agents:
        await agent.set_context(context)

    # Create and run debate session
    session_manager = DebateSessionManager()
    session = await session_manager.create_session(
        council_id=council.council_id,
        topic=selected_topic.to_dict(),
        agents=agents,
        config={
            "max_rounds": 2,
            "voting_enabled": True,
        }
    )

    print(f"📋 Debate session created: {session.session_id}")
    print(f"   Topic: {context.topic}")
    print(f"   Rounds: {session.metadata['max_rounds']}")
    print()

    print("🎤 Starting debate...")
    print()

    # Run the debate
    completed_session = await session_manager.run_debate(
        session_id=session.session_id,
        agents=agents,
        context=context
    )

    print("✅ Debate completed!")
    print()

    input("Press ENTER to view results...")

    # ===================================================================
    # PHASE 4: Results & Transcript
    # ===================================================================
    print_section("PHASE 4: Results & Transcript")

    # Generate and display transcript
    transcript = await session_manager.get_session_transcript(session.session_id)
    print(transcript)

    # ===================================================================
    # PHASE 5: Statistics
    # ===================================================================
    print_section("PHASE 5: System Statistics")

    print("📊 Event Ingestion:")
    print(f"   Twitter: {twitter.get_stats()['events_fetched']} events")
    print(f"   News: {news.get_stats()['events_fetched']} events")
    print()

    print("📊 Processing:")
    print(f"   Events processed: {processor.get_stats()['processed_count']}")
    print(f"   Topics extracted: {extractor.get_stats()['topics_generated']}")
    print()

    print("📊 Council:")
    print(f"   Councils formed: {council_manager.get_stats()['councils_formed']}")
    print()

    print("📊 Debate:")
    print(f"   Sessions run: {session_manager.get_stats()['sessions_created']}")
    print(f"   Duration: {completed_session.outcome['duration']:.0f}s")
    print()

    print("📊 Agents:")
    for agent in agents:
        history = await agent.get_response_history()
        votes = await agent.get_vote_history()
        print(f"   {agent.personality.name}:")
        print(f"      Responses: {len(history)} | Votes: {len(votes)}")
    print()

    # ===================================================================
    # Summary
    # ===================================================================
    print_banner("✅ DEMO COMPLETE")

    print("🎉 Successfully demonstrated:")
    print("   ✅ End-to-end event ingestion pipeline")
    print("   ✅ Automated topic extraction")
    print("   ✅ Diverse council formation")
    print("   ✅ Multi-round structured debate")
    print("   ✅ Agent voting with reasoning")
    print("   ✅ Results tabulation and transcript")
    print()

    print("🚀 The AI Council System prototype is functional!")
    print()
    print("Next steps:")
    print("   • Connect real LLM APIs (Claude, GPT-4)")
    print("   • Integrate live event sources")
    print("   • Add streaming output (TTS + visuals)")
    print("   • Build web interface")
    print("   • Deploy blockchain RNG")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
