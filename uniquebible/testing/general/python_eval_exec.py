# difference between eval and exec
# https://stackoverflow.com/questions/2220699/whats-the-difference-between-eval-exec-and-compile

def func(string):
    return string

code = input("Enter a command line here: ")
exec(code)

expression = input("Enter an expression here: ")
returnValue = eval(expression)
print(returnValue)
