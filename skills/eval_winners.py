import asyncio
import json
import glob
from pathlib import Path
import logging
from datetime import datetime

import sys
sys.path.insert(0, "/home/gamerx/aria/skills")
from self_improve_agent import evaluate_and_pick_winner

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("Eval")

async def main():
    json_files = []
    json_files.extend(glob.glob("/home/gamerx/aria/research/session_20260321_114653/*.json"))
    json_files.extend(glob.glob("/home/gamerx/aria/research/session_20260321_150045/*.json"))
    
    log.info(f"Found {len(json_files)} JSON reports to evaluate.")
    
    all_findings = []
    for f in json_files:
        try:
            with open(f) as file:
                data = json.load(file)
                if "category" not in data:
                    data["category"] = Path(f).stem.replace("_", " ")
                all_findings.append(data)
        except Exception as e:
            log.error(f"Failed to load {f}: {e}")
            
    winners = []
    for findings in all_findings:
        cat = findings.get("category", "Unknown")
        log.info(f"Evaluating: {cat}")
        winner = await evaluate_and_pick_winner(findings)
        if winner:
            winner["category"] = cat
            winners.append(winner)
            log.info(f"  🏆 Winner: {winner['winner_name']} — {winner['reason']}")
        else:
            log.info(f"  ✗ No suitable tool for {cat}")
        
    out_dir = Path("/home/gamerx/aria/research/final_evaluation")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    with open(out_dir / "WINNERS.json", "w") as f:
        json.dump(winners, f, indent=2)
        
    with open(out_dir / "WINNERS.md", "w") as f:
        f.write("# 🏆 ARIA Self-Improvement — Final Selected Winners\n\n")
        f.write(f"**Date:** {datetime.now().isoformat()}\n")
        f.write(f"**Total Evaluated:** {len(all_findings)}\n")
        f.write(f"**Winners Found:** {len(winners)}\n\n")
        f.write("| Category | Winner | Install | Confidence |\n")
        f.write("|---|---|---|---|\n")
        for w in winners:
            f.write(f"| {w['category']} | {w['winner_name']} | `{str(w.get('install_command', 'N/A'))[:50]}` | {w.get('confidence', '?')}/10 |\n")
            
        f.write(f"\n\n## Detailed Picks\n\n")
        for w in winners:
            f.write(f"### {w['category']}\n")
            f.write(f"- **Tool:** {w['winner_name']}\n")
            f.write(f"- **URL:** {w.get('winner_url', 'N/A')}\n")
            f.write(f"- **Install:** `{w.get('install_command', 'N/A')}`\n")
            f.write(f"- **Reason:** {w['reason']}\n\n")
            
    log.info(f"Saved WINNERS.md to {out_dir}")

if __name__ == "__main__":
    asyncio.run(main())
