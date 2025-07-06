parking_lots = []
fetchJSONData();

function onChangeLocality() {    
    locality = document.getElementById("locality").value;   
    filtered_lots = parking_lots.filter(lot => lot.locality === locality && lot.free_spots > 0);
    available = false;
    content = `
        <div class='field'>
            <select name="lot_id" required>
                <option value='' disable select>Select Parking Lot</option>
    `;
    for (lot of filtered_lots) {
        content += `<option value="${lot.lot_id}">${lot.lot_name}</option>`;
    }
    content += `
            </select>
        </div>
        <div class="field">
            <input type="submit" value="Reserve">
        </div>
    `;
    document.getElementById("filter").innerHTML = content;
    
}

function fetchJSONData() {
    fetch('/static/json/data.json')
    .then(response => {
        if (!response.ok) {
        throw new Error("Failed to load JSON");
        }
        return response.json();
    })
    .then(data => {
        parking_lots = data;
        console.log("Loaded JSON:", parking_lots);
    })
    .catch(error => {
        console.error("Error loading JSON:", error);
    });
}