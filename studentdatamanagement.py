stu_dictionary={}

while True:
    
    print("1: Take input in dictionary")
    print("2:display the dictionary")
    print("3:To print a secific roll no")
    print("4:delete the data")
    print("5:Upgrade your dictionary")
    
    
    ch=int(input("Enter your choice:"))
    
    match (ch):
        case 1:
            rollno=int(input("Enter your roll number:"))
            name=input("Enter your name:")
            course=input("Enter your class:")
            age= input("Enter your age:")
            stu_dictionary[rollno]={"Name":name,"Course":course,"Age":age}
        case 2:
            print("Here is your dictionary:",stu_dictionary)
            
        case 3:
            data=input("enter your roll number:")
            data=stu_dictionary[rollno]
            print("This is your data:",stu_dictionary[rollno])
        case 4:
            value=int(input("Enter your Roll No:"))
            if value in stu_dictionary:
             value=stu_dictionary.pop(value)
             print("deleted items are:",value) 
            else:
                print("Not in dictionary")  
        case 5: 
             
            new_name=input("Enter your updated name:")
            new_course=input("Enter your new class:")
            new_age= input("Enter your new age:")
            stu_dictionary[rollno]["Name"]=new_name
            stu_dictionary[rollno]["course"]=new_course
            stu_dictionary[rollno]["age"]=new_age
            print("Data updated")
                
        case _ :
            print("Invalid choice")
        