reservations = []

function loadGraph() {
    localities = [];
    count_data = [];
    for (reservation of reservations) {
        localities.push(reservation['locality']);
        count_data.push(reservation['reservation_count']);
    }
    
    
    const data = {
        labels: localities,
        datasets: [{
            data: count_data,
            backgroundColor: '#4169E1'
        }]
    };

    const config = {
        type: 'bar',
        data: data,
        options: {
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'No. of Reservations',                        
                        color: 'black',
                        padding: {
                            top: 50,
                            bottom: 0
                        },
                        font: {
                            size: 18,
                            family: 'Poppins',
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        display: true,
                        font: {
                            size: 12,
                            family: 'Poppins',
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Locality',
                        color: 'black',
                        padding: {
                            top: 10,
                            bottom: 50
                        },
                        font: {
                            size: 18,
                            family: 'Poppins',
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        display: true,
                        font: {
                            size: 12,
                            family: 'Poppins',
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            },
            responsive: true,
            maintainAspectRatio: false
        },
    };

    const ctx = document.getElementById('reservation_chart').getContext('2d');
    const myChart = new Chart(ctx, config);
    
}

function fetchReservationData() {
    fetch('/static/json/reservation_data.json')
    .then(response => {
        if (!response.ok) {
        throw new Error("Failed to load JSON");
        }
        return response.json();
    })
    .then(data => {
        reservations = data;
        console.log("Loaded JSON:", reservations);
        loadGraph();
    })
    .catch(error => {
        console.error("Error loading JSON:", error);
    });
}