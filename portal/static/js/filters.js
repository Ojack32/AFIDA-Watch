// Simple map filter interactivity
document.addEventListener('DOMContentLoaded', function() {
    const stateFilter = document.getElementById('state-filter');
    const metricFilter = document.getElementById('metric-filter');
    
    if (stateFilter) {
        stateFilter.addEventListener('change', function() {
            console.log('State filter changed to:', this.value);
            // In production, this would reload the map with filtered data
        });
    }
    
    if (metricFilter) {
        metricFilter.addEventListener('change', function() {
            console.log('Metric filter changed to:', this.value);
            // In production, this would update the choropleth coloring
        });
    }
});
