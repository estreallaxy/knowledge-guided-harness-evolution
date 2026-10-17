//! Utility functions and helpers

use serde::{Deserialize, Serialize};
use std::time::{Duration, Instant};

/// Metrics collector for PSE system
#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct Metrics {
    /// Total entity registrations
    pub total_registrations: u64,
    /// Total entity lookups
    pub total_lookups: u64,
    /// Total events emitted
    pub total_events: u64,
    /// Total hook executions
    pub total_hook_executions: u64,
    /// Total propagations
    pub total_propagations: u64,
    /// Average lookup latency (microseconds)
    pub avg_lookup_latency_us: f64,
    /// Average hook execution latency (microseconds)
    pub avg_hook_execution_latency_us: f64,
    /// Propagation depth histogram
    pub propagation_depth_histogram: Vec<u64>,
}

/// Timer for measuring operation latency
pub struct Timer {
    start: Instant,
}

impl Timer {
    pub fn start() -> Self {
        Self {
            start: Instant::now(),
        }
    }

    pub fn elapsed(&self) -> Duration {
        self.start.elapsed()
    }

    pub fn elapsed_micros(&self) -> u64 {
        self.elapsed().as_micros() as u64
    }

    pub fn elapsed_millis(&self) -> u64 {
        self.elapsed().as_millis() as u64
    }
}

/// Generate a unique trace ID
pub fn generate_trace_id() -> String {
    uuid::Uuid::new_v4().to_string()
}

/// Serialize value to pretty JSON
pub fn to_pretty_json<T: Serialize>(value: &T) -> Result<String, serde_json::Error> {
    serde_json::to_string_pretty(value)
}

/// Calculate edit distance between two sequences (for tool call comparison)
pub fn edit_distance<T: PartialEq>(a: &[T], b: &[T]) -> usize {
    let m = a.len();
    let n = b.len();

    if m == 0 {
        return n;
    }
    if n == 0 {
        return m;
    }

    let mut dp = vec![vec![0usize; n + 1]; m + 1];

    for i in 0..=m {
        dp[i][0] = i;
    }
    for j in 0..=n {
        dp[0][j] = j;
    }

    for i in 1..=m {
        for j in 1..=n {
            let cost = if a[i - 1] == b[j - 1] { 0 } else { 1 };
            dp[i][j] = (dp[i - 1][j] + 1)
                .min(dp[i][j - 1] + 1)
                .min(dp[i - 1][j - 1] + cost);
        }
    }

    dp[m][n]
}

/// Normalized edit distance (0.0 to 1.0)
pub fn normalized_edit_distance<T: PartialEq>(a: &[T], b: &[T]) -> f64 {
    let max_len = a.len().max(b.len());
    if max_len == 0 {
        return 0.0;
    }
    edit_distance(a, b) as f64 / max_len as f64
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_edit_distance() {
        assert_eq!(edit_distance(&[1, 2, 3], &[1, 2, 3]), 0);
        assert_eq!(edit_distance(&[1, 2, 3], &[1, 2, 4]), 1);
        assert_eq!(edit_distance(&[1, 2, 3], &[4, 5, 6]), 3);
        assert_eq!(edit_distance::<i32>(&[], &[1, 2, 3]), 3);
    }

    #[test]
    fn test_normalized_edit_distance() {
        assert!((normalized_edit_distance(&[1, 2, 3], &[1, 2, 3]) - 0.0).abs() < 0.001);
        assert!((normalized_edit_distance(&[1, 2, 3], &[4, 5, 6]) - 1.0).abs() < 0.001);
    }
}
