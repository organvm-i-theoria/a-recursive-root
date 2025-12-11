"""
Viewer Voting System Demo

This demo showcases the real-time viewer voting system integrated
with the AI Council debates.

Features demonstrated:
- Viewer vote submission
- Real-time vote aggregation
- Combining agent and viewer votes
- Gamification (points, achievements, leaderboards)
- Voting statistics and analytics
"""

import asyncio
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web.backend.voting.voting_api import VoteType, VotePosition, get_voting_manager
from web.backend.voting.gamification import get_gamification_manager, ACHIEVEMENTS, AchievementType
from core.council.viewer_integration import get_viewer_integration_manager


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_section(title: str):
    """Print a section header"""
    print(f"\n--- {title} ---\n")


async def simulate_agent_votes():
    """Simulate agent votes for a debate"""
    # 5 agents voting on a topic
    agent_votes = {
        "agent_pragmatist": VotePosition.SUPPORT,
        "agent_idealist": VotePosition.SUPPORT,
        "agent_skeptic": VotePosition.OPPOSE,
        "agent_analyst": VotePosition.NEUTRAL,
        "agent_optimist": VotePosition.SUPPORT,
    }

    return agent_votes


async def main():
    """Run the viewer voting demo"""

    print_header("🗳️  Viewer Voting System Demo")

    # Get managers
    viewer_mgr = get_viewer_integration_manager()
    voting_mgr = get_voting_manager()
    gamification_mgr = get_gamification_manager()

    # Demo configuration
    debate_id = "debate_ai_regulation_2025"
    topic = "Should AI be heavily regulated by governments?"
    description = "Debate on the appropriate level of government regulation for AI development and deployment"
    topic_category = "technology"

    # ========================================
    # 1. Open Debate for Viewer Voting
    # ========================================

    print_section("1. Opening Debate for Viewer Voting")

    await viewer_mgr.open_debate_for_voting(
        debate_id=debate_id,
        topic=topic,
        description=description,
        vote_type=VoteType.BINARY
    )

    print(f"📣 Debate Opened!")
    print(f"   Topic: {topic}")
    print(f"   ID: {debate_id}")
    print(f"   Vote Type: Binary (Support/Oppose)")

    # ========================================
    # 2. Simulate Viewer Votes
    # ========================================

    print_section("2. Simulating Viewer Votes")

    # Create diverse viewer votes
    viewer_votes = [
        # Strongly support regulation
        {"user_id": "user_alice", "position": VotePosition.SUPPORT, "confidence": 0.95,
         "reasoning": "AI poses significant risks that require oversight"},
        {"user_id": "user_bob", "position": VotePosition.SUPPORT, "confidence": 0.85,
         "reasoning": "We need safeguards to protect public interest"},
        {"user_id": "user_charlie", "position": VotePosition.SUPPORT, "confidence": 0.75,
         "reasoning": "Balance between innovation and safety is crucial"},

        # Oppose regulation
        {"user_id": "user_diana", "position": VotePosition.OPPOSE, "confidence": 0.90,
         "reasoning": "Over-regulation will stifle innovation"},
        {"user_id": "user_eve", "position": VotePosition.OPPOSE, "confidence": 0.80,
         "reasoning": "Market forces can self-regulate better"},

        # Neutral/Cautious
        {"user_id": "user_frank", "position": VotePosition.NEUTRAL, "confidence": 0.50,
         "reasoning": "Need more information before deciding"},
        {"user_id": "user_grace", "position": VotePosition.SUPPORT, "confidence": 0.60,
         "reasoning": "Some regulation needed, but not too heavy"},

        # Additional support votes
        {"user_id": "user_henry", "position": VotePosition.SUPPORT, "confidence": 0.70},
        {"user_id": "user_iris", "position": VotePosition.SUPPORT, "confidence": 0.80},
        {"user_id": "user_jack", "position": VotePosition.OPPOSE, "confidence": 0.75},
    ]

    print(f"💬 Submitting {len(viewer_votes)} viewer votes...\n")

    for vote_data in viewer_votes:
        vote = await viewer_mgr.submit_viewer_vote(
            user_id=vote_data["user_id"],
            debate_id=debate_id,
            round_number=1,
            position=vote_data["position"],
            confidence=vote_data.get("confidence", 0.5),
            reasoning=vote_data.get("reasoning"),
            topic_category=topic_category
        )

        position_icon = "✅" if vote.position == VotePosition.SUPPORT else "❌" if vote.position == VotePosition.OPPOSE else "🤔"
        print(f"   {position_icon} {vote_data['user_id']}: {vote.position.value.upper()} "
              f"(confidence: {vote.confidence:.0%})")

    # ========================================
    # 3. Display Vote Statistics
    # ========================================

    print_section("3. Viewer Vote Statistics")

    stats = await voting_mgr.get_stats(debate_id)

    if stats:
        print(f"📊 Total Votes: {stats.total_votes}")
        print(f"   ✅ Support: {stats.support_votes} ({stats.support_percentage:.1f}%)")
        print(f"   ❌ Oppose: {stats.oppose_votes} ({stats.oppose_percentage:.1f}%)")
        print(f"   🤔 Neutral: {stats.neutral_votes}")
        print(f"\n   Average Confidence: {stats.avg_confidence:.0%}")
        print(f"   Consensus Level: {stats.consensus_level:.0%}")
        print(f"   Vote Velocity: {stats.vote_velocity:.1f} votes/min")

        if stats.top_reasons:
            print(f"\n   📝 Top Reasons:")
            for i, reason in enumerate(stats.top_reasons[:3], 1):
                print(f"      {i}. {reason}")

    # ========================================
    # 4. Simulate Agent Votes
    # ========================================

    print_section("4. Agent Votes")

    agent_votes = await simulate_agent_votes()

    print("🤖 AI Agents have voted:")
    for agent_id, position in agent_votes.items():
        position_icon = "✅" if position == VotePosition.SUPPORT else "❌" if position == VotePosition.OPPOSE else "🤔"
        print(f"   {position_icon} {agent_id}: {position.value.upper()}")

    agent_support = sum(1 for v in agent_votes.values() if v == VotePosition.SUPPORT)
    agent_oppose = sum(1 for v in agent_votes.values() if v == VotePosition.OPPOSE)
    print(f"\n   Agent Outcome: {agent_support} Support, {agent_oppose} Oppose")

    # ========================================
    # 5. Calculate Hybrid Result
    # ========================================

    print_section("5. Hybrid Result (Agents + Viewers)")

    # Set weights (agents 70%, viewers 30%)
    viewer_mgr.set_vote_weights(agent_weight=0.7, viewer_weight=0.3)

    hybrid_result = await viewer_mgr.calculate_hybrid_result(
        debate_id=debate_id,
        round_number=1,
        agent_votes=agent_votes
    )

    print("🎯 Vote Weights:")
    print(f"   🤖 Agents: {hybrid_result.agent_weight:.0%}")
    print(f"   👥 Viewers: {hybrid_result.viewer_weight:.0%}")

    print("\n📈 Individual Outcomes:")
    print(f"   Agents Only: {hybrid_result.agent_outcome.value.upper()}")
    print(f"   Viewers Only: {hybrid_result.viewer_outcome.value.upper()}")

    print(f"\n🏆 FINAL OUTCOME: {hybrid_result.final_outcome.value.upper()}")
    print(f"   Support Score: {hybrid_result.final_support_score:.2%}")
    print(f"   Oppose Score: {hybrid_result.final_oppose_score:.2%}")
    print(f"   Consensus Level: {hybrid_result.consensus_level:.0%}")

    print(f"\n   Total Votes: {hybrid_result.agent_votes + hybrid_result.viewer_votes}")
    print(f"   - Agents: {hybrid_result.agent_votes}")
    print(f"   - Viewers: {hybrid_result.viewer_votes}")

    # ========================================
    # 6. Finalize and Award Points
    # ========================================

    print_section("6. Finalizing Debate & Awarding Points")

    await viewer_mgr.finalize_debate_voting(
        debate_id=debate_id,
        final_outcome=hybrid_result.final_outcome
    )

    print("🎁 Gamification points awarded!")
    print("   ✓ Accurate prediction bonuses")
    print("   ✓ Participation points")
    print("   ✓ Achievement checks completed")

    # ========================================
    # 7. User Profiles & Achievements
    # ========================================

    print_section("7. User Profiles & Achievements")

    # Show profile for Alice (first voter)
    alice_profile = await gamification_mgr.get_profile("user_alice")

    if alice_profile:
        print(f"👤 Profile: {alice_profile.user_id}")
        print(f"   Points: {alice_profile.points} 🏆")
        print(f"   Reputation: {alice_profile.reputation_tier.value.upper()}")
        print(f"   Total Votes: {alice_profile.total_votes}")
        print(f"   Current Streak: {alice_profile.current_streak} days 🔥")
        print(f"   Accuracy Rate: {alice_profile.accuracy_rate:.1f}%")

        if alice_profile.achievements:
            print(f"\n   🎖️  Achievements Unlocked ({len(alice_profile.achievements)}):")
            for achievement_type in alice_profile.achievements:
                achievement = ACHIEVEMENTS[achievement_type]
                print(f"      {achievement.badge_icon} {achievement.name} - {achievement.description}")

        if alice_profile.next_tier:
            print(f"\n   🎯 Next Goal: {alice_profile.next_tier.value.upper()}")
            print(f"      {alice_profile.points_to_next_tier} points to go!")

    # ========================================
    # 8. Leaderboard
    # ========================================

    print_section("8. Leaderboard")

    leaderboard = await gamification_mgr.get_leaderboard(limit=5, sort_by="points")

    print("🏆 Top Voters by Points:\n")
    for entry in leaderboard:
        medal = "🥇" if entry.rank == 1 else "🥈" if entry.rank == 2 else "🥉" if entry.rank == 3 else "  "
        print(f"   {medal} #{entry.rank} {entry.user_id}")
        print(f"       {entry.points} pts | {entry.reputation_tier.value} | "
              f"{entry.total_votes} votes | {entry.achievement_count} achievements")

    # ========================================
    # 9. Advanced Analytics
    # ========================================

    print_section("9. Advanced Analytics")

    viewer_stats = await viewer_mgr.get_viewer_stats(debate_id)

    print("📊 Viewer Engagement Metrics:")
    print(f"   Participation Rate: {(viewer_stats['total_votes'] / 10) * 100:.0f}% (10 simulated viewers)")
    print(f"   Average Confidence: {viewer_stats['avg_confidence']:.0%}")
    print(f"   Consensus Quality: {viewer_stats['consensus_level']:.0%}")
    print(f"   Engagement Velocity: {viewer_stats['vote_velocity']:.1f} votes/min")

    # ========================================
    # Summary
    # ========================================

    print_header("✅ Demo Complete!")

    print("Summary:")
    print(f"   • {stats.total_votes} viewer votes collected")
    print(f"   • {len(agent_votes)} agent votes simulated")
    print(f"   • Hybrid outcome calculated with {viewer_mgr.agent_weight:.0%}/{viewer_mgr.viewer_weight:.0%} weighting")
    print(f"   • Gamification points and achievements awarded")
    print(f"   • {len(leaderboard)} users on leaderboard")

    print("\nKey Features Demonstrated:")
    print("   ✓ Real-time vote submission and aggregation")
    print("   ✓ Multi-position voting (support/oppose/neutral)")
    print("   ✓ Confidence-based voting")
    print("   ✓ Optional reasoning for votes")
    print("   ✓ Agent + Viewer vote integration")
    print("   ✓ Gamification (points, achievements, streaks)")
    print("   ✓ Leaderboards and rankings")
    print("   ✓ Advanced analytics and metrics")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
