
customers = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@gmail.com"
    },
    {
        "id": 2,
        "first_name": "JJ",
        "last_name": "Lumibao",
        "email": "jjlumibao@gmail.com"
    },
    {
        "id": 3,
        "first_name": "Ervin",
        "last_name": "Gordon",
        "email": "ervingordon@gmail.com"
    },
    {
        "id": 4,
        "first_name": "Aadib",
        "last_name": "Uddin",
        "email": "aadibuddin@gmail.com"
    },
    {
        "id": 5,
        "first_name": "Dustin",
        "last_name": "Allen",
        "email": "dustinallen@gmail.com"
    },
]


def create_customer(customer_data: dict) -> dict:
   # 1. Generate a new ID based on current list length
   new_id = len(customers) + 1
  
   # 2. Assign the ID to the dictionary
   customer_data["id"] = new_id
  
   # 3. Append to global list
   customers.append(customer_data)
  
   # 4. Return the newly created record
   return customer_data


def get_customers_by_id(customer_id: int) -> dict:
   #iterates through the list of customers and returns the customer with the matching ID
   for customer in customers:
       #Verifys is the customer ID matches the ID passed in the fuction
       if customer["id"] == customer_id:
           return customer
   #If the customer ID is not found in the list, raise a ValueError   
   raise ValueError(f"Customer with ID {customer_id} not found.")


def update_customer(customer_id: int, updated_data: dict) -> dict:
   #Iterates through the list of customers and updates the customer with the matching ID
   for customer in customers:
       if customer["id"] == customer_id:
           #Updates the customer data with the new data passed in the function
           customer.update(updated_data)
           return customer
   #If the customer ID is not found in the list, raise a ValueError
   raise ValueError(f"Customer with ID {customer_id} not found.")


def deactivate_customer(customer_id: int):
   #Iterates through the list of customers and deactivates the customer with the matching ID
   for customer in customers:
       if customer["id"] == customer_id:
           #Sets the active status of the customer to False
           customer["active"] = False
           return customer
