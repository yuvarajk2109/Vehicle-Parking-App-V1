function onChangeUpdateParamater() {
    parameter = document.getElementById("parameter").value;
    console.log(parameter);
    content = '';
    if (parameter === 'lot_name') {
         content = `
            <div class="field">
                <input type="text" name="lot_name" required>
                <label for="lot_name">New Lot Name</label>
            </div>
        `;
    } else if (parameter === 'address') {
        content = `
            <div class="field">
                <textarea name="address" required></textarea>
                <label for="address">New Address</label>
            </div>
            <br><br>
            <div class="field">
                <input type="text" name="locality" required>
                <label for="locality">New Locality</label>
            </div>
            <div class="field">
                <input type="text" name="pincode" required>
                <label for="pincode">New Pincode</label>
            </div>
        `;
    } else if (parameter === 'base_price') {
        content = `
            <div class="field">
                <input type="text" name="base_price" required>
                <label for="base_price">Base Price</label>
            </div>
        `;
    } else if (parameter === 'additional_price') {
        content = `
            <div class="field">
                <input type="text" name="additional_price" required>
                <label for="additional_price">Additional Price</label>
            </div>
        `;
    } else if (parameter === 'total_spots') {
        content = `
             <div class="field">
                <input type="number" name="total_spots" required>
                <label for="total_spots">Total No. of Spots</label>
            </div>
        `;
    }
    content += `
        <div class="field">
            <input type="submit" value="Update">
        </div>
    `;
    document.getElementById("update").innerHTML = content;
}