#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  ARIA Self-Improvement Engine — Master Orchestrator          ║
║  Chains: Deep Research → Evaluate → Install → Test → Learn  ║
║                                                               ║
║  This is the meta-agent that makes ARIA evolve autonomously. ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    # Full auto-improvement sweep (all 25 categories, ~2-5 hours):
    python3 self_improve_agent.py --full

    # Research a single capability:
    python3 self_improve_agent.py --category "computer vision OCR"

    # Research + auto-install winners:
    python3 self_improve_agent.py --full --auto-install

    # Research only (no installation):
    python3 self_improve_agent.py --full --research-only
"""
import asyncio
import json
import sys
import logging
import argparse
import re
from pathlib import Path
from datetime import datetime

# Import sister agents
sys.path.insert(0, str(Path(__file__).parent))
from deep_research_agent import run_full_research, research_category, DEFAULT_CATEGORIES, llm_analyze, SYSTEM_SPECS
from genesis_agent import genesis

ARIA_DIR = Path.home() / "aria"
RESEARCH_DIR = ARIA_DIR / "research"
SKILLS_DIR = ARIA_DIR / "skills"
UPGRADE_LOG = RESEARCH_DIR / "upgrade_history.json"

log = logging.getLogger("SelfImprove")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


async def evaluate_and_pick_winner(findings: dict) -> dict | None:
    """Use the LLM to pick the single best tool from research findings."""
    category = findings["category"]
    # Use the 3-pass analysis from deep_research_agent
    llm_summary = findings.get("llm_final_recommendations", "") or findings.get("llm_deep_analysis", "")
    
    repos = findings.get("github_repos", [])
    repo_list = "\n".join([
        f"- {r['name']} (★{r['stars']}, {r['language']}): {r['description']}"
        for r in repos[:10]
    ])
    
    prompt = f"""You are a systems integration architect. Based on this research for "{category}":

{SYSTEM_SPECS}

RESEARCH SUMMARY:
{llm_summary[:3000]}

GITHUB REPOS FOUND:
{repo_list}

YOUR TASK: Pick the ONE BEST tool that:
1. Works natively on Arch Linux / Wayland
2. Is actively maintained (updated in last 6 months)  
3. Has a clear CLI or Python API
4. Uses minimal resources (≤8GB VRAM, ≤16GB RAM)
5. Is free and open source

Respond in EXACT JSON format (no markdown, no explanation):
{{
    "winner_name": "tool-name",
    "winner_repo": "github-org/repo-name or N/A",
    "winner_url": "https://...",
    "install_command": "exact command to install on Arch Linux",
    "reason": "one sentence why this is the best choice",
    "confidence": 8
}}

If NO suitable tool was found for this category, respond:
{{"winner_name": "NONE", "reason": "explanation"}}"""

    response = await llm_analyze(prompt)
    
    # Parse JSON from response
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            if result.get("winner_name") and result["winner_name"] != "NONE":
                return result
            else:
                log.info(f"  No suitable tool found for {category}: {result.get('reason', 'unknown')}")
                return None
    except json.JSONDecodeError as e:
        log.error(f"  Failed to parse LLM evaluation: {e}")
        log.error(f"  Raw response: {response[:500]}")
    return None


async def run_self_improvement(categories: list[dict], auto_install: bool = False, research_only: bool = False):
    """The master orchestration loop."""
    start_time = datetime.now()
    log.info("╔══════════════════════════════════════════════════╗")
    log.info("║  ARIA Self-Improvement Engine — STARTING         ║")
    log.info(f"║  Categories: {len(categories)}")
    log.info(f"║  Mode: {'Research Only' if research_only else 'Full Auto-Install' if auto_install else 'Research + Manual Install'}")
    log.info(f"║  Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("╚══════════════════════════════════════════════════╝")
    
    # Phase 1: Deep Research
    log.info("\n" + "="*60)
    log.info("PHASE 1: DEEP RESEARCH")
    log.info("="*60)
    
    all_findings, output_dir = await run_full_research(categories)
    
    if research_only:
        log.info("\n✓ Research-only mode. Results saved. Exiting.")
        return
    
    # Phase 2: Evaluate Winners
    log.info("\n" + "="*60)
    log.info("PHASE 2: EVALUATING WINNERS")
    log.info("="*60)
    
    winners = []
    for findings in all_findings:
        cat = findings["category"]
        log.info(f"\nEvaluating: {cat}")
        
        winner = await evaluate_and_pick_winner(findings)
        if winner:
            winner["category"] = cat
            winners.append(winner)
            log.info(f"  🏆 Winner: {winner['winner_name']} — {winner['reason']}")
        else:
            log.info(f"  ✗ No suitable tool for {cat}")
        
        await asyncio.sleep(1)
    
    # Save winners report
    winners_file = output_dir / "WINNERS.json"
    with open(winners_file, "w") as f:
        json.dump(winners, f, indent=2)
    
    winners_md = output_dir / "WINNERS.md"
    with open(winners_md, "w") as f:
        f.write("# 🏆 ARIA Self-Improvement — Selected Winners\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Total Categories Researched:** {len(categories)}\n")
        f.write(f"**Winners Found:** {len(winners)}\n\n")
        f.write("| Category | Winner | Install | Confidence |\n")
        f.write("|---|---|---|---|\n")
        for w in winners:
            f.write(f"| {w['category']} | {w['winner_name']} | `{w.get('install_command', 'N/A')[:50]}` | {w.get('confidence', '?')}/10 |\n")
        f.write(f"\n\n## Detailed Picks\n\n")
        for w in winners:
            f.write(f"### {w['category']}\n")
            f.write(f"- **Tool:** {w['winner_name']}\n")
            f.write(f"- **URL:** {w.get('winner_url', 'N/A')}\n")
            f.write(f"- **Install:** `{w.get('install_command', 'N/A')}`\n")
            f.write(f"- **Reason:** {w['reason']}\n\n")
    
    log.info(f"\n✓ Winners report saved to {winners_md}")
    
    if not auto_install:
        log.info("\n⚠ Auto-install disabled. Review WINNERS.md and run genesis manually.")
        log.info(f"   python3 genesis_agent.py --tool-name <name> --category <cat> --install-cmd <cmd>")
        return
    
    # Phase 3: Genesis (Auto-Install + Skill Creation)
    log.info("\n" + "="*60)
    log.info("PHASE 3: GENESIS — INSTALLING & CREATING SKILLS")
    log.info("="*60)
    
    results = []
    for winner in winners:
        cat = winner["category"]
        tool = winner["winner_name"]
        install_cmd = winner.get("install_command", "")
        
        log.info(f"\n{'─'*40}")
        log.info(f"Genesis: {tool} for [{cat}]")
        log.info(f"{'─'*40}")
        
        result = await genesis(tool, cat, install_cmd)
        results.append(result)
        
        if result["test_passed"]:
            log.info(f"  ✓ {tool} fully integrated!")
        else:
            log.warning(f"  ⚠ {tool} partially integrated (tests failed)")
        
        await asyncio.sleep(2)
    
    # Save final upgrade log
    end_time = datetime.now()
    upgrade_entry = {
        "session_start": start_time.isoformat(),
        "session_end": end_time.isoformat(),
        "duration_minutes": (end_time - start_time).total_seconds() / 60,
        "categories_researched": len(categories),
        "winners_found": len(winners),
        "skills_created": sum(1 for r in results if r["skill_created"]),
        "tests_passed": sum(1 for r in results if r["test_passed"]),
        "results": results,
    }
    
    # Append to upgrade history
    history = []
    if UPGRADE_LOG.exists():
        try:
            with open(UPGRADE_LOG) as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append(upgrade_entry)
    with open(UPGRADE_LOG, "w") as f:
        json.dump(history, f, indent=2)
    
    # Print final summary
    duration = (end_time - start_time).total_seconds() / 60
    log.info("\n" + "="*60)
    log.info("SELF-IMPROVEMENT SESSION COMPLETE")
    log.info("="*60)
    log.info(f"  Duration: {duration:.1f} minutes")
    log.info(f"  Categories researched: {len(categories)}")
    log.info(f"  Winners found: {len(winners)}")
    log.info(f"  Skills created: {sum(1 for r in results if r['skill_created'])}")
    log.info(f"  Tests passed: {sum(1 for r in results if r['test_passed'])}")
    log.info(f"  Research dir: {output_dir}")
    log.info("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ARIA Self-Improvement Engine")
    parser.add_argument("--full", action="store_true", help="Run full sweep across all 25 categories")
    parser.add_argument("--category", type=str, help="Research a single category")
    parser.add_argument("--auto-install", action="store_true", help="Auto-install winners after research")
    parser.add_argument("--research-only", action="store_true", help="Research only, no installation")
    
    args = parser.parse_args()
    
    if args.category:
        categories = [{"name": args.category, "description": args.category}]
    elif args.full:
        categories = DEFAULT_CATEGORIES
    else:
        parser.print_help()
        print("\nExamples:")
        print('  python3 self_improve_agent.py --full --research-only')
        print('  python3 self_improve_agent.py --full --auto-install')
        print('  python3 self_improve_agent.py --category "computer vision OCR" --auto-install')
        sys.exit(0)
    
    asyncio.run(run_self_improvement(categories, auto_install=args.auto_install, research_only=args.research_only))
