import sys                                                               
import time                                                              
import tracemalloc                                                       
import csv                                                               
from pathlib import Path                                                 
import matplotlib        
matplotlib.use("Agg")   
import matplotlib.pyplot as plt                                          
                                                                         
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))             
                                                                         
from source.task2_competitive.competitive_state import CompetitiveState  
from source.task2_competitive.competitive_engine import CompetitiveEngine
from source.task2_competitive.agent1 import Agent1                       
from source.task2_competitive.agent2 import Agent2                       
                                         
MAP_PATH = "maps/competitive_map.txt"                                    
MAX_TURNS = 100 
NUM_MATCHES = 10

def run_match(initial_state, max_turns):                         
    engine = CompetitiveEngine(initial_state.clone(), max_turns)
    agent1 = Agent1()
    agent2 = Agent2()

    times = {1: [], 2: []}                                                      
    peaks = {1: [], 2: []}                                                      
                                                                                 
    while not engine.finished:                                                  
        snapshot = engine.state.clone()                                         
        actions = {}                                                            
                                                                                
        for agent_id, agent in ((1, agent1), (2, agent2)):              
            tracemalloc.start()
            start = time.perf_counter()                                         
                                                                                
            actions[agent_id] = agent.choose_action(snapshot.clone(), time_limit=0.9)
            elapsed_ms = (time.perf_counter() - start) * 1000
            _, peak_bytes = tracemalloc.get_traced_memory()                     
            tracemalloc.stop()          
            times[agent_id].append(elapsed_ms)                                  
            peaks[agent_id].append(peak_bytes / 1024)                           
                                                                                 
        engine.step(actions)

    return {                                                                    
        "turns": engine.state.turn,                                             
        "score1": engine.state.score(1),                                        
        "score2": engine.state.score(2),                                        
        "winner": engine.state.winner(),                                        
        "avg_time1_ms": sum(times[1]) / len(times[1]),                          
        "avg_time2_ms": sum(times[2]) / len(times[2]),                          
        "avg_peak1_kb": sum(peaks[1]) / len(peaks[1]),                          
        "avg_peak2_kb": sum(peaks[2]) / len(peaks[2]),                          
    }

def main():                                                                     
    root = Path(__file__).resolve().parents[2]                                  
    initial_state = CompetitiveState.from_file(root / MAP_PATH)                 
                                                                                
    rows = []                                                                   
    for match_id in range(NUM_MATCHES):                                         
        result = run_match(initial_state, MAX_TURNS)                            
        result["match"] = match_id                                              
        rows.append(result)                                                     
        print(match_id, result)                                                 
                                                                                
    fieldnames = [                                                              
        "match", "turns", "score1", "score2", "winner",                         
        "avg_time1_ms", "avg_time2_ms", "avg_peak1_kb", "avg_peak2_kb",         
    ]

    out_path = root / "docs" / "experiments" / "agents_results.csv"             
    with open(out_path, "w", newline="", encoding="utf-8") as f:                
        writer = csv.DictWriter(f, fieldnames=fieldnames)                                            
        writer.writeheader()                                                    
        writer.writerows(rows)                                                  
                                                                                
    wins1 = sum(1 for r in rows if r["winner"] == 1)                            
    wins2 = sum(1 for r in rows if r["winner"] == 2)                            
    draws = sum(1 for r in rows if r["winner"] is None)                         
                                                                                
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))                             
                                                                                
    axes[0].bar(["Agent1 (A*)", "Agent2 (GBFS)", "Draw"], [wins1, wins2, draws])                                                                         
    axes[0].set_title(f"Win count over {NUM_MATCHES} matches")

    avg_time1 = sum(r["avg_time1_ms"] for r in rows) / len(rows)                
    avg_time2 = sum(r["avg_time2_ms"] for r in rows) / len(rows)                
    axes[1].bar(["Agent1 (A*)", "Agent2 (GBFS)"], [avg_time1, avg_time2])       
    axes[1].set_ylabel("ms")                                                    
    axes[1].set_title("Avg decision time per turn")                             
                                                                                
    avg_peak1 = sum(r["avg_peak1_kb"] for r in rows) / len(rows)                
    avg_peak2 = sum(r["avg_peak2_kb"] for r in rows) / len(rows)                
    axes[2].bar(["Agent1 (A*)", "Agent2 (GBFS)"], [avg_peak1, avg_peak2])       
    axes[2].set_ylabel("KB")                                                    
    axes[2].set_title("Avg peak memory per decision")                           
                                                                                
    fig.tight_layout()                                                          
    fig.savefig(root / "docs" / "experiments" / "agents_results.png")           
                                                                                
                                                                                
if __name__ == "__main__":                                                      
    main()