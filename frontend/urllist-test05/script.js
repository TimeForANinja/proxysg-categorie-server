document.addEventListener("DOMContentLoaded", function() {
    const customSelects = document.querySelectorAll(".custom-select");

    function updateSelectedOptions(customSelect) {
        const selectedOptions = Array.from(customSelect.querySelectorAll(".option.active"))
                .filter(option => option !== customSelect.querySelector(".option.all-tags"))
                .map(option => (
                    {
                        value: option.getAttribute("data-value"),
                        text: option.textContent.trim(),
                    }
                ));

        const selectedValues = selectedOptions.map(option => option.value)

        customSelect.querySelector(".tags_input").value = selectedValues.join(', ');

        let tagsHTML = "";

        if(selectedOptions.length === 0) {
            tagsHTML = '<span class="placeholder">Select the tags</span>'
        } else {
            const maxTagsToShow = 4;
            let additionalTagsCount = 0;

            selectedOptions.forEach((option, index) => {
                if (index < maxTagsToShow) {
                    tagsHTML += '<span class="tag">' +option.text+ '<span class="remove-tag" data-value="' +option.value+ '">&times;</span></span>'
                } else {
                    additionalTagsCount++;
                }
            })

            if (additionalTagsCount > 0) {
                tagsHTML += '<span class="tag">+' +additionalTagsCount+ '</span>'
            }
        }

        customSelect.querySelector(".selected-options").innerHTML = tagsHTML;
    }

    customSelects.forEach(customSelect => {
        const searchInput = customSelect.querySelector('.search-tags');
        const optionsContainer = customSelect.querySelector(".options");
        const noResultMessage = customSelect.querySelector(".no-result-message");
        const options = customSelect.querySelectorAll(".option");
        const allTagsOption = customSelect.querySelector(".option.all-tags");
        const clearButton = customSelect.querySelector(".clear");

        allTagsOption.addEventListener("click", () => {
            const isActive = allTagsOption.classList.contains("active");

            options.forEach(option => {
                if (option !== allTagsOption) {
                    option.classList.toggle("active", !isActive)
                }
            })

            updateSelectedOptions(customSelect)
        })

        clearButton.addEventListener('click', () => {
            searchInput.value = '';
            options.forEach(option => {
                option.style.display = 'block';
            })
            noResultMessage.style.display = 'none';
        })

        searchInput.addEventListener('input', () => {
            const searchTerm = searchInput.value.toLowerCase();

            options.forEach(option => {
                const optionText = option.textContent.trim().toLocaleLowerCase();
                const shouldShow = optionText.includes(searchTerm);
                option.style.display = shouldShow ? 'block' : 'none';
            })

            const anyOptionsMatch = Array.from(options).some(option => option.style.display === 'block');
            noResultMessage.style.display = anyOptionsMatch ? 'none' : 'block';

            if(searchTerm) {
                optionsContainer.classList.add('option-search-active');
            } else {
                optionsContainer.classList.remove('option-search-active')
            }
        })
    })

    customSelects.forEach(customSelect => {
        const options = customSelect.querySelectorAll('.option');
        options.forEach(option => {
            option.addEventListener('click', () => {
                option.classList.toggle('active');
                updateSelectedOptions(customSelect)
            })
        })
    })

    document.addEventListener('click', (event) => {
        const removeTag = event.target.closest(".remove-tag");
        if (removeTag) {
            const customSelect = removeTag.closest(".custom-select");
            const valueToRemove = removeTag.getAttribute("data-value");
            const optionToRemove = customSelect.querySelector(".option[data-value='" +valueToRemove+ "']");
            optionToRemove.classList.remove('active');

            const otherSelectedOptions = customSelect.querySelectorAll('.option.active:not(.all-tags)');
            const allTagsOption = customSelect.querySelector('.option.all-tags');

            if (otherSelectedOptions.length === 0) {
                allTagsOption.classList.remove('active');
            }
            updateSelectedOptions(customSelect);
        }
    });

    const selectBoxes = document.querySelectorAll('.select-box');
    selectBoxes.forEach(selectBox => {
        selectBox.addEventListener('click', (event) => {
            if (!event.target.closest('.tag')) {
                selectBox.parentNode.classList.toggle('open');
            }
        })
    })

    document.addEventListener('click', event => {
        if (!event.target.closest('.custom-select') && !event.target.classList.contains('remove-tag')) {
            customSelects.forEach(customSelect => {
                customSelect.classList.remove('open');
            });
        }
    })

    function resetCustomSelects() {
        customSelects.forEach(customSelect => {
            customSelect.querySelectorAll('.option.active').forEach(option => {
                option.classList.remove('active');
            })
            customSelect.querySelector('.options.all-tags').classList.remove('active');
            updateSelectedOptions(customSelect)
        })
    }
    updateSelectedOptions(customSelects[0]);

    const submitButton = document.querySelector('.btn_submit');
    submitButton.addEventListener('click', () => {
        let valid = true;

        customSelects.forEach(customSelect => {
            const selectedOptions = customSelect.querySelectorAll('.option.active');
            if (selectedOptions.length === 0) {
                const tagErrorMsg = customSelect.querySelector('.tag_error_msg');
                tagErrorMsg.textContent = 'This field is required';
                tagErrorMsg.style.display = 'block';
                valid = false;
            } else {
                const tagErrorMsg = customSelect.querySelector('.tag_error_msg');
                tagErrorMsg.textContent = '';
                tagErrorMsg.style.display = 'none';
            }
        })

        if (valid){
            let tags = document.querySelector('.tags_input').value;
            alert(tags);
            resetCustomSelects();
            return;
        }
    })
});
