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

I need also to create an abstract class for data reader. For json reader shouldn't return array, but use **yield** to return one by one line of text s


## Some details
I'm add suffex to every function name for generate output for output.
I think if i use fn like first generated token for model, model will begin generation
with fn and than will use only functions name if i constraion output.
