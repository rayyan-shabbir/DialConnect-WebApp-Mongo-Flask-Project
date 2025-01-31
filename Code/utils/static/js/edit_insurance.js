
function toggleFieldInput(selectElement) {
    const row = selectElement.closest('tr');
    const actionField = row.querySelector('input[name^="action_"]');
    const customFieldInput = row.querySelector('.custom-field');

    if (selectElement.value === 'other') {
        // Remove the select dropdown and show the custom input field
        selectElement.style.display = 'none';
        customFieldInput.style.display = 'inline-block';
        customFieldInput.required = true; // Make custom field required
        actionField.readOnly = false; // Make action field writable
        actionField.required = true;
        customFieldInput.focus(); // Set focus on the custom field
    } else {
        // Revert the dropdown visibility and hide the custom field input
        selectElement.style.display = 'inline-block';
        customFieldInput.style.display = 'none';
        customFieldInput.value = ''; // Clear the custom field value
        customFieldInput.required = false;
        actionField.readOnly = true;
        actionField.required = false;
    }
}

function addRow() {
    const tableBody = document.getElementById('infoTable').getElementsByTagName('tbody')[0];
    const rowCount = tableBody.rows.length + 1;
    const row = tableBody.insertRow();

    row.innerHTML = `
        <td><input type="text" value="${rowCount}" readonly></td>
        <td>
            <select name="field_${rowCount}" onchange="toggleFieldInput(this)">
                <option value="PolicyNum">Policy Number</option>
                <option value="DOB">Date of Birth</option>
                <option value="NPI">National Provider Identifier (NPI)</option>
                <option value="DOS">Date of Service</option>
                <option value="Tax">Tax</option>
                <option value="other">Other</option>
            </select>
            <input type="text" class="custom-field" name="custom_field_${rowCount}" style="display:none;" placeholder="Enter custom field">
        </td>
        <td><input type="text" name="sentence_${rowCount}" placeholder="Enter sentence" required></td>
        <td><input type="text" name="action_${rowCount}" placeholder="Enter action" readonly></td>
        <td>
            <select name="callback_${rowCount}" required>
                <option value="" selected disabled>Select Callback</option>
                <option value="Audio">Audio</option>
                <option value="Keypad">Keypad</option>
            </select>
        </td>
        <td>
            <!-- Remove button with Bootstrap styling -->
            <button type="button" class="btn btn-danger btn-sm" onclick="removeRow(this)">Remove</button>
        </td>
    `;
}

function removeRow(button) {
    const row = button.closest('tr');
    const tableBody = document.getElementById('infoTable').getElementsByTagName('tbody')[0];
    const rowIndex = Array.from(tableBody.rows).indexOf(row);

    // Remove the row
    row.remove();

    // Update the indices of the remaining rows
    for (let i = rowIndex; i < tableBody.rows.length; i++) {
        const currentRow = tableBody.rows[i];
        const srInput = currentRow.querySelector('input[type="text"]:first-child');
        srInput.value = i + 1;

        // Update the name attributes of the inputs
        const inputs = currentRow.querySelectorAll('input, select');
        inputs.forEach(input => {
            const name = input.name;
            const newName = name.replace(/_\d+/, `_${i + 1}`);
            input.name = newName;
        });
    }
}


function goHomeUser() {
    window.location.href = '/user_table';  // Adjust the URL to your homepage
}


function goHomeAdmin() {
    window.location.href = '/admin_table';  // Adjust the URL to your homepage
}
