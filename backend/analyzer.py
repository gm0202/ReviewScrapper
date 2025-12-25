from typing import List, Dict, Any
import pandas as pd

def analyze_trends(daily_stats_map: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
    """
    Analyzes daily stats to produce the trend matrix, new topics list, and spike list.
    
    daily_stats_map: { "2025-01-01": {"topic1": 10}, "2025-01-02": {"topic1": 20, "topic2": 5} }
    """
    
    # 1. Build DataFrame
    # Rows: Topics, Cols: Dates
    # Accumulate all unique topics
    all_topics = set()
    for date, stats in daily_stats_map.items():
        all_topics.update(stats.keys())
        
    dates = sorted(daily_stats_map.keys())
    
    # Structure: {topic: [count_d1, count_d2, ...]}
    trend_matrix = {topic: [] for topic in all_topics}
    
    for date in dates:
        stats = daily_stats_map.get(date, {})
        for topic in all_topics:
            trend_matrix[topic].append(stats.get(topic, 0))
            
    # 2. Detect New Topics & Spikes
    # Logic:
    # New: Present in the LAST date, but 0 in all previous dates.
    # Spike: Count in LAST date > 2 * (Avg of previous dates or just prev date). Using prev date for simplicity as per spec.
    
    new_topics = []
    spikes = []
    
    if len(dates) >= 1:
        latest_date_idx = len(dates) - 1
        
        for topic, counts in trend_matrix.items():
            current_count = counts[latest_date_idx]
            
            # Simple check: ignore very small counts to reduce noise
            if current_count < 2:
                continue
            
            # New Topic Check
            if len(dates) > 1:
                prev_counts = counts[:latest_date_idx]
                if sum(prev_counts) == 0:
                    new_topics.append(topic)
            
            # Spike Check
            if len(dates) > 1:
                prev_count = counts[latest_date_idx - 1]
                # Avoid division by zero, treat 0->N (large N) as new, but if prev was small...
                # Spec: count_today > 2 * count_previous
                if prev_count > 0:
                    if current_count > 2 * prev_count:
                        spikes.append(topic)
                elif prev_count == 0 and current_count >= 5: # If 0 -> 5, considered spike/new
                     spikes.append(topic)

    # Sort trend matrix by total volume descending
    sorted_topics = sorted(trend_matrix.keys(), key=lambda t: sum(trend_matrix[t]), reverse=True)
    sorted_trend_matrix = {t: trend_matrix[t] for t in sorted_topics}

    return {
        "trend_matrix": sorted_trend_matrix,
        "new_topics": new_topics,
        "spikes": peaks_check(spikes, new_topics), # Helper cleanup
        "dates": dates
    }

def peaks_check(spikes, new_topics):
    # Remove topics from spikes if they are already in new_topics to avoid double badging
    return [s for s in spikes if s not in new_topics]
