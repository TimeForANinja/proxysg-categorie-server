// my-select.js
class MySelect extends HTMLElement {
    constructor() {
        super();

        // Attach a shadow DOM
        const shadow = this.attachShadow({ mode: 'open' });

        // Create a container element
        const container = document.createElement('div');
        container.setAttribute('class', 'container');

        // Create a label element
        const label = document.createElement('label');
        label.setAttribute('for', 'select');
        label.textContent = this.getAttribute('label') || 'Select an option:';

        // Create a select element
        const select = document.createElement('select');
        select.setAttribute('id', 'select');
        select.setAttribute('name', 'select');

        // Populate the select element with options
        const options = JSON.parse(this.getAttribute('options') || '[]');
        options.forEach(optionData => {
            const option = document.createElement('option');
            option.value = optionData.value;
            option.textContent = optionData.label;
            select.appendChild(option);
        });

        // Attach event listeners
        select.addEventListener('change', (event) => {
            this.dispatchEvent(new CustomEvent('change', {
                detail: { value: event.target.value }
            }));
        });

        // Append elements to the container
        container.appendChild(label);
        container.appendChild(select);

        // Create some CSS to apply to the shadow DOM
        const style = document.createElement('style');
        style.textContent = `
      .container {
        display: flex;
        flex-direction: column;
        font-family: Arial, sans-serif;
      }
      label {
        margin-bottom: 5px;
      }
      select {
        padding: 5px;
        font-size: 14px;
      }
    `;

        // Attach the created elements to the shadow DOM
        shadow.appendChild(style);
        shadow.appendChild(container);
    }
}

// Define the new element
customElements.define('my-select', MySelect);
