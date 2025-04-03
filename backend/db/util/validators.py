from marshmallow.validate import Regexp


simpleNameRegex = r"^[a-zA-Z0-9_-]+$"
simpleNameError = "Only alphanumeric, underscores and hyphens are allowed."
simpleNameValidator = Regexp(simpleNameRegex, error=simpleNameError)

simpleStringRegex = r"^[0-9A-Za-z !#$%&()*\-.\/:;=?@[\]_|~]*$"
simpleStringError = "Only ASCII excluding some control characters is allowed."
simpleStringValidator = Regexp(simpleStringRegex, error=simpleStringError)

simpleURLRegex = r"^([a-zA-Z0-9_-]+\.)+([a-zA-Z0-9_-]+)$"
simpleURLError = "URLs must be in format <host or subdomain>.<domain> and consist of alphanumeric, underscores and hyphens."
simpleURLValidator = Regexp(simpleURLRegex, error=simpleURLError)
