print("*******CALCULATOR***********")

x=float(input("Enter your first number:"))
y=float(input("Enter your second number:"))
operator=input("Enter your operator(+,_,*,/):").strip()
match operator:
    case "+": 
        result= x+y
        #print("Your answer is:",result)
    case "-":
        if y>x:print("can't be solved")
        else:result=x-y
        #print("Your answer is:",result)
    case "*":
         result=x*y
         #print("Your answer is:",result)
    case "/":
              if y==0:print("can't be solved")
              else:result=x/y
              #print("Your answer is:",result)
              
    case _: print("invalid operator")
         
print("Your answer is:",result)      
         
            
            
    
    