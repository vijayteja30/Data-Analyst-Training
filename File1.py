def print_loop():
    for i in range(10):
        print(i)


class PrintLoop:
    def __init__(self):
        self.count = 10

    def print_loop(self):
        for i in range(self.count):
            print(i)

def main():
    print("Using procedural approach:")
    print_loop()
    print("\nUsing OOP approach:")
    loop = PrintLoop()
    loop.print_loop()

class Product:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def display(self):
        print(f"Product Name: {self.name}, Price: {self.price}")
    
    def product_reviews(self, reviews):
        print(f"Reviews for {self.name}:")
        for review in reviews:
            print(f"- {review}")
    def product_rating(self, rating):
        print(f"Rating for {self.name}: {rating} stars")
obj = Product()
obj.display()
if __name__ == "__main__":
    main()