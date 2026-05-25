# Force-injection
## First aspect

If I can extract two digits, then I can allow the model to use only certain types of tokens (in this case only name of functions).
If no digits are found, then it could be a function that doesn't require digits.
Then I need to move on to the next aspect.

# Second
If I need to extract some data, like a user's name, then:
I can constrain the model to use only tokens from the user input.
Then I can use these tokens to parse the user data.

## Some hints

Make work line mask replacement:


Flow:

(It could be done with go language)
ReadInput (Get prompt from user) -> Buildprompt -> FindSomeFunction -> CallFunction  