document.addEventListener('DOMContentLoaded', function () {
    function toggleSidebar() {
        document.querySelector('.sidebar').classList.toggle('open');
    }

    let fieldCounter = 0;

    function addField() {
        fieldCounter++;

        const fieldOptions = `
            <option value="PolicyNum">Policy Number</option>
            <option value="NPI">National Provider Identifier (NPI)</option>
            <option value="DOB">Date of Birth</option>
            <option value="DOS">Date of Service</option>
            <option value="Tax">Tax</option>
            <option value="other">Other</option>
        `;

        const newField = `
            <div class="row mb-3" id="field-group-${fieldCounter}">
                <div class="col-md-3">
                    <label for="field-${fieldCounter}" class="form-label">Select Field</label>
                    <div class="input-group">
                        <select class="form-select" id="field-${fieldCounter}" name="field_${fieldCounter}" required onchange="handleFieldChange(${fieldCounter})">
                            ${fieldOptions}
                        </select>
                        <input type="text" class="form-control inp" id="custom_field-${fieldCounter}" name="custom_field_${fieldCounter}" placeholder="Enter custom field name" style="display: none;">
                    </div>
                </div>
                <div class="col-md-3">
                    <label for="sentence-${fieldCounter}" class="form-label">Sentence</label>
                    <input type="text" class="form-control" id="sentence-${fieldCounter}" name="sentence_${fieldCounter}" required placeholder="Enter Sentence">
                </div>
                <div class="col-md-3">
                    <label for="action-${fieldCounter}" class="form-label">Action</label>
                    <input type="text" class="form-control" id="action-${fieldCounter}" name="action_${fieldCounter}" placeholder="Enter Action" readonly required>
                </div>
                <div class="col-md-3">
                    <label for="callback-${fieldCounter}" class="form-label">Callback</label>
                    <div class="input-group">
                        <select class="form-select" id="callback-${fieldCounter}" name="callback_${fieldCounter}" required>
                            <option value="" selected disabled>Select Field</option>
                            <option value="Audio">Audio</option>
                            <option value="Keypad">Keypad</option>
                        </select>
                        <button type="button" class="btn btn-danger btn-sm ms-2 remove" onclick="removeField(${fieldCounter})">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('dynamic-fields').insertAdjacentHTML('beforeend', newField);
    }

    function handleFieldChange(counter) {
        const selectedField = document.getElementById(`field-${counter}`).value;
        const actionField = document.getElementById(`action-${counter}`);
        const customFieldInput = document.getElementById(`custom_field-${counter}`);
        const inputGroup = document.querySelector(`#field-group-${counter} .input-group`);

        if (selectedField === 'other') {
            // Make the action field editable and remove readonly attribute
            actionField.readOnly = false;
            actionField.value = ''; // Clear the field if it had any value

            // Remove the existing dropdown and replace with custom input field
            inputGroup.innerHTML = `
                <input type="text" class="form-control" id="custom_field-${counter}" name="custom_field_${counter}" placeholder="Enter custom field name" required>
            `;

            // Set focus on the new custom input field
            document.getElementById(`custom_field-${counter}`).focus();
        } else {
            // Revert the action field to readonly and clear its value
            actionField.readOnly = true;
            actionField.value = ''; // Clear the action field

            // Revert to original dropdown if 'Other' is not selected
            inputGroup.innerHTML = `
                <select class="form-select" id="field-${counter}" name="field_${counter}" required onchange="handleFieldChange(${counter})">
                    <option value="PolicyNum" ${selectedField === 'PolicyNum' ? 'selected' : ''}>Policy Number</option>
                    <option value="NPI" ${selectedField === 'NPI' ? 'selected' : ''}>National Provider Identifier (NPI)</option>
                    <option value="DOB" ${selectedField === 'DOB' ? 'selected' : ''}>Date of Birth</option>
                    <option value="DOS" ${selectedField === 'DOS' ? 'selected' : ''}>Date of Service</option>
                    <option value="Tax" ${selectedField === 'Tax' ? 'selected' : ''}>Tax</option>
                    <option value="other" ${selectedField === 'other' ? 'selected' : ''}>Other</option>
                </select>
            `;
        }
    }

    function removeField(counter) {
        const fieldGroup = document.getElementById(`field-group-${counter}`);
        if (fieldGroup) {
            fieldGroup.remove();
        }
    }

    function showSuccessAlert(message) {
        const alertBox = document.createElement('div');
        alertBox.classList.add('custom-alert', 'alert', 'alert-success');
        alertBox.innerText = message;

        document.body.appendChild(alertBox);

        setTimeout(() => {
            alertBox.remove();
        }, 3000);
    }

    // Handle form submission and show success alert
    document.getElementById('insurance-form').addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission

        // Perform the form submission via AJAX or other methods here

        // Show success alert
        showSuccessAlert('Dial Plan Submit successful');
    });

    window.addField = addField;
    window.handleFieldChange = handleFieldChange;
    window.removeField = removeField;
    window.showSuccessAlert = showSuccessAlert;
});
