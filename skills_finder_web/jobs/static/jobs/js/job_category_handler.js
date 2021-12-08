function redirectToCorrectChartByChosenJobCategory() {
    window.location.href = `show-chart?job-category=${document.getElementById("selected_job_category").value}`;
}
