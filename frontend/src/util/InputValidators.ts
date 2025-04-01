export const isRequiredError = "This field is required."

export const simpleNameRegex = /^[a-zA-Z0-9_-]+$/
export const simpleNameError = "Only alphanumeric, underscores and hyphens are allowed."
export const simpleNameCheck = (
    value: string,
    required: boolean = false,
) => {
    if (required && value.length === 0) {
        return isRequiredError
    }

    if (!simpleNameRegex.test(value)) {
        return simpleNameError;
    }

    return null;
}

export const simpleStringRegex = /^[a-zA-Z0-9 _-]*$/
export const simpleStringError = "Only alphanumeric, underscores, hyphens and spaces are allowed."
export const simpleStringCheck = (
    value: string,
    required: boolean = false,
) => {
    if (required && value.length === 0) {
        return isRequiredError;
    }

    if (!simpleStringRegex.test(value)) {
        return simpleStringError;
    }

    return null;
}

export const simpleURLRegex = /^([a-zA-Z0-9_-]+\.)+([a-zA-Z0-9_-]+)$/
export const simpleURLError = "URLs must be in format <host or subdomain>.<domain> and consist of alphanumeric, underscores and hyphens."
export const simpleURLCheck = (
    value: string,
    required: boolean = false,
) => {
    if (required && value.length === 0) {
        return isRequiredError
    }

    if (!simpleURLRegex.test(value)) {
        return simpleURLError;
    }

    return null;
}
